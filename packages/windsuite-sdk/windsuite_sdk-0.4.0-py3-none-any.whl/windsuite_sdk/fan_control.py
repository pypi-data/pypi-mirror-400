from __future__ import annotations

import time
from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum
from typing import Any

import requests
from loguru import logger


class ModuleType(Enum):
    MODULE_2420 = "2420"
    MODULE_0816 = "0816"


@dataclass
class ModuleConfig:
    module_type: ModuleType
    row: int
    col: int
    mac: str | None = None

    @property
    def num_layers(self) -> int:
        return 2 if self.module_type == ModuleType.MODULE_0816 else 1

    @property
    def fans_per_layer(self) -> int:
        return 9 if self.module_type == ModuleType.MODULE_0816 else 1

    @property
    def fan_grid_rows(self) -> int:
        """Number of fan rows in this module type (3 for 0816, 1 for 2420)."""
        return 3 if self.module_type == ModuleType.MODULE_0816 else 1

    @property
    def fan_grid_cols(self) -> int:
        """Number of fan columns in this module type (3 for 0816, 1 for 2420)."""
        return 3 if self.module_type == ModuleType.MODULE_0816 else 1


class MachineLayout:
    def __init__(self, nb_rows: int, nb_columns: int, api_url: str | None = None):
        self.nb_rows = nb_rows
        self.nb_columns = nb_columns
        self.api_url = api_url
        self.modules: dict[tuple[int, int], ModuleConfig] = {}
        self.fan_states: dict[tuple[int, int, int, int], float] = {}
        self.modified_modules: set[tuple[int, int]] = set()
        self.flat_index_map: dict[tuple[int, int], int] = {}

    def add_module(
        self, row: int, col: int, module_type: ModuleType, flat_index: int | None = None, mac: str | None = None
    ) -> None:
        if row < 0 or row >= self.nb_rows:
            raise ValueError(f"Row {row} out of bounds [0, {self.nb_rows})")
        if col < 0 or col >= self.nb_columns:
            raise ValueError(f"Column {col} out of bounds [0, {self.nb_columns})")

        config = ModuleConfig(module_type, row, col, mac=mac)
        self.modules[(row, col)] = config

        if flat_index is not None:
            self.flat_index_map[(row, col)] = flat_index
        else:
            self.flat_index_map[(row, col)] = row * self.nb_columns + col

        for layer in range(config.num_layers):
            for fan_idx in range(config.fans_per_layer):
                self.fan_states[(row, col, layer, fan_idx)] = 0.0

    def get_module(self, row: int, col: int) -> ModuleConfig | None:
        return self.modules.get((row, col))

    def get_module_by_mac(self, mac: str) -> tuple[int, int] | None:
        """Get (row, col) for a module by its MAC address."""
        for (row, col), config in self.modules.items():
            if config.mac == mac:
                return (row, col)
        return None

    def set_fan_pwm(self, row: int, col: int, layer: int, fan_index: int, pwm: float) -> None:
        pwm = max(0.0, min(100.0, pwm))
        self.fan_states[(row, col, layer, fan_index)] = pwm
        self.modified_modules.add((row, col))

    def get_fan_pwm(self, row: int, col: int, layer: int, fan_index: int) -> float:
        return self.fan_states.get((row, col, layer, fan_index), 0.0)

    @classmethod
    def from_dict(cls, windcontrol_layout: dict[str, Any], api_url: str | None = None) -> MachineLayout:
        """Create a MachineLayout from a windcontrol_layout dictionary."""
        size_x = windcontrol_layout["size_x"]
        size_y = windcontrol_layout["size_y"]
        module_grid = windcontrol_layout["module_grid"]

        layout = cls(nb_rows=size_y, nb_columns=size_x, api_url=api_url)

        for flat_idex_str, module_data in module_grid.items():
            flat_index = int(flat_idex_str)
            row = module_data["grid_index_y"]
            col = module_data["grid_index_x"]
            module_type_str = module_data["module_type"]
            mac = module_data.get("mac")

            if module_type_str == "2420":
                module_type = ModuleType.MODULE_2420
            elif module_type_str == "0816":
                module_type = ModuleType.MODULE_0816
            else:
                continue

            layout.add_module(row, col, module_type, flat_index=flat_index, mac=mac)

        return layout

    @classmethod
    def from_api(cls, api_url: str) -> MachineLayout:
        url = f"{api_url.rstrip('/')}/windcontrol/layouts/"
        response = requests.get(url, timeout=5)
        response.raise_for_status()

        data = response.json()
        windcontrol_layout = data["current_windcontrol_layout"]

        return cls.from_dict(windcontrol_layout, api_url=api_url)


class FanControlBuilder:
    COOLDOWN_SECONDS: float = 1.0

    def __init__(self, layout: MachineLayout):
        self.layout = layout
        self._last_error_time: float = 0.0
        self._reset_selection()

    def _reset_selection(self) -> None:
        self._selected_rows: list[int] | None = None
        self._selected_cols: list[int] | None = None
        self._selected_layer: int | None = None
        self._selected_fans: list[int] | None = None
        self._selected_parity: int | None = None  # 0 = even, 1 = odd

    def _convert_index(self, index: int, max_val: int) -> int:
        """Convert potentially negative 1-based index to positive 1-based index."""
        if index < 0:
            return max_val + index + 1
        return index

    def _validate_index(self, index: int, max_val: int, name: str) -> None:
        """Validate a single 1-based index (supports negative indexing)."""
        if index == 0:
            raise ValueError(f"{name} index cannot be zero")
        if index > max_val or index < -max_val:
            raise ValueError(f"{name} index {index} out of bounds for layout with {max_val} {name.lower()}s")

    def _validate_indices(self, indices: list[int], max_val: int, name: str) -> None:
        """Validate a list of 1-based indices (supports negative indexing)."""
        if not indices:
            raise ValueError(f"'{name}' list cannot be empty")
        if any(i == 0 for i in indices):
            raise ValueError(f"'{name}' list cannot contain zero")
        if any(i > max_val or i < -max_val for i in indices):
            raise ValueError(f"'{name}' list contains out of bounds indices for layout with {max_val} {name.lower()}s")

    def _validate_range(self, from_val: int, to_val: int, max_val: int, name: str) -> None:
        """Validate from/to range parameters (supports negative indexing)."""
        if any(v == 0 for v in (from_val, to_val)):
            raise ValueError(f"'from_{name}' and 'to_{name}' cannot be zero")
        if any(v > max_val or v < -max_val for v in (from_val, to_val)):
            raise ValueError(f"'from_{name}' or 'to_{name}' out of bounds for layout with {max_val} {name}s")

    def rows(
        self,
        rows: list[int] | None = None,
        from_row: int | None = None,
        to_row: int | None = None,
    ) -> FanControlBuilder:
        """
        Select specific rows or a range of rows.

        Args:
            rows (list[int] | None): List of 1-based row indices to select.
            from_row (int | None): 1-based starting row index for range selection.
            to_row (int | None): 1-based ending row index for range selection.

        Notes:
            - Negative indices are supported (e.g., -1 refers to the last row).
            - Either 'rows' or 'from_row'/'to_row' should be provided, not both.
            - If using range selection, both 'from_row' and 'to_row' must be specified.

        """
        if rows is not None and (from_row is not None or to_row is not None):
            raise ValueError("Cannot use both 'rows' and 'from_row/to_row' parameters")

        nb_rows = self.layout.nb_rows
        if rows is not None:
            self._validate_indices(rows, nb_rows, "rows")
            self._selected_rows = [self._convert_index(r, nb_rows) - 1 for r in rows]
        elif from_row is not None and to_row is not None:
            self._validate_range(from_row, to_row, nb_rows, "row")
            from_conv = self._convert_index(from_row, nb_rows)
            to_conv = self._convert_index(to_row, nb_rows)
            if to_conv < from_conv:
                raise ValueError("'to_row' must be greater than or equal to 'from_row' after index conversion")
            self._selected_rows = list(range(from_conv - 1, to_conv))
        elif from_row is not None or to_row is not None:
            raise ValueError("Both 'from_row' and 'to_row' must be specified for range")

        return self

    def row(self, row: int) -> FanControlBuilder:
        """
        Select a specific single row. (use rows() to select multiple rows)

        Args:
            row (int): 1-based row index to select.

        Notes:
            - Negative indices are supported (e.g., -1 refers to the last row).

        """
        nb_rows = self.layout.nb_rows
        self._validate_index(row, nb_rows, "Row")
        self._selected_rows = [self._convert_index(row, nb_rows) - 1]
        return self

    def columns(
        self,
        columns: list[int] | None = None,
        from_col: int | None = None,
        to_col: int | None = None,
    ) -> FanControlBuilder:
        """
        Select specific columns or a range of columns.

        Args:
            columns (list[int] | None): List of 1-based column indices to select.
            from_col (int | None): 1-based starting column index for range selection.
            to_col (int | None): 1-based ending column index for range selection.

        Notes:
            - Negative indices are supported (e.g., -1 refers to the last column).
            - Either 'columns' or 'from_col'/'to_col' should be provided, not both.
            - If using range selection, both 'from_col' and 'to_col' must be specified.

        """
        if columns is not None and (from_col is not None or to_col is not None):
            raise ValueError("Cannot use both 'columns' and 'from_col/to_col' parameters")

        nb_columns = self.layout.nb_columns
        if columns is not None:
            self._validate_indices(columns, nb_columns, "columns")
            self._selected_cols = [self._convert_index(c, nb_columns) - 1 for c in columns]
        elif from_col is not None and to_col is not None:
            self._validate_range(from_col, to_col, nb_columns, "col")
            from_conv = self._convert_index(from_col, nb_columns)
            to_conv = self._convert_index(to_col, nb_columns)
            if to_conv < from_conv:
                raise ValueError("'to_col' must be greater than or equal to 'from_col' after index conversion")
            self._selected_cols = list(range(from_conv - 1, to_conv))
        elif from_col is not None or to_col is not None:
            raise ValueError("Both 'from_col' and 'to_col' must be specified for range")

        return self

    def column(self, column: int) -> FanControlBuilder:
        nb_columns = self.layout.nb_columns
        self._validate_index(column, nb_columns, "Column")
        self._selected_cols = [self._convert_index(column, nb_columns) - 1]
        return self

    def even_modules(self) -> FanControlBuilder:
        """
        Select modules where (row + col) is even (checkerboard pattern).

        This creates a checkerboard selection starting with (0,0).
        Modules at positions like (0,0), (0,2), (1,1), (2,0), (2,2) are selected.

        Returns:
            FanControlBuilder: The builder instance for method chaining.

        """
        self._selected_parity = 0
        return self

    def odd_modules(self) -> FanControlBuilder:
        """
        Select modules where (row + col) is odd (checkerboard pattern).

        This creates a checkerboard selection opposite to even_modules().
        Modules at positions like (0,1), (1,0), (1,2), (2,1) are selected.

        Returns:
            FanControlBuilder: The builder instance for method chaining.

        """
        self._selected_parity = 1
        return self

    def downstream(self) -> FanControlBuilder:
        """
        Select the downstream layer (layer 0) for multi-layer modules (e.g. 0816).

        Note: This is used when you want to control the downstream layer only.
        If not set, all layers will be affected.
        Modules with only 1 layer will not be affected by this setting.

        Returns:
            FanControlBuilder: The builder instance for method chaining.

        """
        self._selected_layer = 0
        return self

    def upstream(self) -> FanControlBuilder:
        """
        Select the upstream layer (layer 1) for multi-layer modules (e.g. 0816).

        Note: This is used when you want to control the upstream layer only.
        If not set, all layers will be affected.
        Modules with only 1 layer will not be affected by this setting.

        Returns:
            FanControlBuilder: The builder instance for method chaining.

        """
        self._selected_layer = 1
        return self

    def fans(self, fans: list[int]) -> FanControlBuilder:
        """
        Select specific fans within selected modules.

        Args:
            fans (list[int]): List of 1-based fan indices to select.

        Notes:
            - Negative indices are NOT supported for fan selection.
            - You only need to use this method if you DON'T want to select all fans in the module.
            - If a module has fewer fans than specified, only the valid fans will be affected.
            - single fan modules will ignore and always be selected.

            - Fan indices start at 1 for the first fan in a module:
            ┌─────┬─────┬─────┐
            │  1  │  2  │  3  │
            ├─────┼─────┼─────┤
            │  4  │  5  │  6  │
            ├─────┼─────┼─────┤
            │  7  │  8  │  9  │
            └─────┴─────┴─────┘

        """
        if not fans:
            raise ValueError("fans list cannot be empty")
        if any(f == 0 for f in fans):
            raise ValueError("fans list cannot contain zero (use 1-based indexing)")
        if any(f < 0 for f in fans):
            raise ValueError("fans list cannot contain negative indices")
        self._selected_fans = [f - 1 for f in fans]
        return self

    def set_intensity(self, percent: float | list[float] | list[list[float]]) -> FanControlBuilder:
        """
        Set the intensity for the currently selected fans.

        Args:
            percent (float | list[float] | list[list[float]]): Intensity percentage(s) to set (0.0-100.0).
                - Single float: applies to all selected fans.
                - 1D list: spreads horizontally or vertically across modules (or fans if dimensions match).
                - 2D list matching module dimensions: one value per module.
                - 2D list matching fan grid dimensions: one value per fan (auto-detected).

        """
        rows = self._resolve_rows()
        cols = self._resolve_cols()

        # Get fan grid info for detection
        fan_grid_rows, fan_grid_cols, fan_rows_per_module, fan_cols_per_module, is_homogeneous = self._get_fan_grid_info(
            rows, cols
        )

        # Detect pattern level
        pattern_level = self._detect_pattern_level(percent, len(rows), len(cols), fan_grid_rows, fan_grid_cols)

        if pattern_level == "fan" and is_homogeneous:
            # Fan-level application
            fan_matrix = self._normalize_to_fan_matrix(percent, fan_grid_rows, fan_grid_cols)
            self._apply_fan_level_matrix(fan_matrix, rows, cols, fan_rows_per_module, fan_cols_per_module)
        else:
            # Module-level application (existing behavior)
            matrix = self._normalize_to_matrix(percent, len(rows), len(cols))

            for row_idx, row in enumerate(rows):
                for col_idx, col in enumerate(cols):
                    module = self.layout.get_module(row, col)
                    if module is None:
                        continue

                    # Check parity filter (checkerboard pattern)
                    if self._selected_parity is not None and (row + col) % 2 != self._selected_parity:
                        continue

                    pwm_value = matrix[row_idx][col_idx]
                    layers = self._resolve_layers(module)
                    fan_indices = self._resolve_fans(module)

                    for layer in layers:
                        for fan_idx in fan_indices:
                            self.layout.set_fan_pwm(row, col, layer, fan_idx, pwm_value)

        self._reset_selection()
        return self

    def set_intensity_func(self, func: Callable[[float, float], float]) -> FanControlBuilder:
        """
        Set intensity using a function of normalized position.

        Args:
            func: Callable (x, y) -> intensity where:
                - x: normalized column position (0.0 = left, 1.0 = right)
                - y: normalized row position (0.0 = top, 1.0 = bottom)
                - returns: intensity value (0.0-100.0), will be clamped

        Returns:
            FanControlBuilder for method chaining

        """
        rows = self._resolve_rows()
        cols = self._resolve_cols()

        # Calculate normalization factors (handle single row/col edge case)
        max_row = self.layout.nb_rows - 1 if self.layout.nb_rows > 1 else 1
        max_col = self.layout.nb_columns - 1 if self.layout.nb_columns > 1 else 1

        for row in rows:
            for col in cols:
                module = self.layout.get_module(row, col)
                if module is None:
                    continue

                # Check parity filter
                if self._selected_parity is not None and (row + col) % 2 != self._selected_parity:
                    continue

                # Normalize positions to 0-1
                x = col / max_col
                y = row / max_row

                # Call user function and clamp result
                intensity = max(0.0, min(100.0, func(x, y)))

                layers = self._resolve_layers(module)
                fan_indices = self._resolve_fans(module)

                for layer in layers:
                    for fan_idx in fan_indices:
                        self.layout.set_fan_pwm(row, col, layer, fan_idx, intensity)

        self._reset_selection()
        return self

    def apply(self, dry_run: bool = False) -> dict[str, dict[str, dict[str, list[int]]]] | None:
        """
        Apply the currently set fan intensity settings to the actual API

        Args:
            dry_run (bool): If True, will not send to API but return the payload instead

        Returns:
            The payload sent to the API, or None if an acceptable error occurred or in cooldown
                dict[str, dict[str, dict[str, list[int]]]] | None

        """
        if not self.layout.api_url:
            raise ValueError("API URL not set. Cannot apply changes to API.")

        # Check cooldown after layout mismatch
        if time.monotonic() - self._last_error_time < self.COOLDOWN_SECONDS:
            return None

        pwm_data: dict[str, dict[str, list[int]]] = {}

        for row, col in self.layout.modified_modules:
            module = self.layout.get_module(row, col)
            if not module:
                continue

            flat_index = self.layout.flat_index_map.get((row, col))
            if flat_index is None:
                continue

            flat_idex_str = str(flat_index)
            pwm_data[flat_idex_str] = {}

            for layer in range(module.num_layers):
                layer_pwms: list[int] = []
                for fan_idx in range(module.fans_per_layer):
                    pwm_pct = self.layout.get_fan_pwm(row, col, layer, fan_idx)
                    pwm_int = round(pwm_pct * 10)
                    layer_pwms.append(pwm_int)

                pwm_data[flat_idex_str][str(layer)] = layer_pwms

        payload = {"pwm_data": pwm_data}

        if dry_run:
            return payload

        url = f"{self.layout.api_url.rstrip('/')}/windcontrol/modules/pwms"
        response = requests.patch(url, json=payload, timeout=5)
        if response.status_code == 400:
            logger.warning("Layout mismatch - fan control skipped (layout may be updating)")
            self._last_error_time = time.monotonic()
            self.layout.modified_modules.clear()
            return None
        response.raise_for_status()
        self.layout.modified_modules.clear()

        return payload

    """
    Date: 09/01/2026
    Jonas Stirnemann

    Pattern Spreading Algorithm

    A bit complex, hard to explain concisely, but here's the gist:

    When calling set_intensity(percent), the system auto-detects whether to apply
    values at MODULE-level or FAN-level based on input dimensions.

    Detection rules (for 2x2 modules of 3x3 fans = 6x6 fan grid):
        Input exceeds module dimensions? -> FAN-level (spread/truncate to fan grid)
        Otherwise                        -> MODULE-level (spread to module grid)

    Examples:
        Input         Detection    Action
        -----         ---------    ------
        50.0          module       Same value for all fans
        [[a,b]]       module       2 cols <= 2 modules -> module-level, spread to 2x2
        [[a,b,c]]     fan          3 cols > 2 modules -> fan-level, spread to 6x6
        [[...],[...]] (2x2)        module       Matches module grid exactly
        [[...],[...],[...]] (3x6)  fan          Exceeds modules -> spread 3 rows to 6
        [[...]] (1x5)              fan          5 > 2 modules -> spread to 6x6

    Spreading algorithm:
        When input is smaller than target, values are repeated to fill:

        [A, B, C] spread to 6 cols:
            repeat_factor = 6 // 3 = 2
            remainder = 6 % 3 = 0
            Result: [A, A, B, B, C, C]

        [A, B, C] spread to 5 cols:
            repeat_factor = 5 // 3 = 1
            remainder = 5 % 3 = 2
            Result: [A, A, B, B, C]  (first 2 values get extra copy)

        When input is larger than target, values are truncated:
            [A, B, C, D, E] to 3 fans cols -> [A, B, C]

    """

    def _resolve_rows(self) -> list[int]:
        if self._selected_rows is not None:
            return self._selected_rows
        return list(range(self.layout.nb_rows))

    def _resolve_cols(self) -> list[int]:
        if self._selected_cols is not None:
            return self._selected_cols
        return list(range(self.layout.nb_columns))

    def _resolve_layers(self, module: ModuleConfig) -> list[int]:
        if self._selected_layer is not None:
            if module.num_layers > 1:
                return [self._selected_layer]
            return [0]
        return list(range(module.num_layers))

    def _resolve_fans(self, module: ModuleConfig) -> list[int]:
        if self._selected_fans is not None:
            if module.fans_per_layer > 1:
                valid_fans = [fan_idx for fan_idx in self._selected_fans if 0 <= fan_idx < module.fans_per_layer]
                return valid_fans if valid_fans else [0]
            return [0]
        return list(range(module.fans_per_layer))

    def _get_fan_grid_info(self, rows: list[int], cols: list[int]) -> tuple[int, int, int, int, bool]:
        """
        Calculate fan grid dimensions for the selected modules.

        Returns:
            tuple of (total_fan_rows, total_fan_cols, fan_rows_per_module,
                      fan_cols_per_module, is_homogeneous)

        """
        fan_rows_per_module: int | None = None
        fan_cols_per_module: int | None = None
        is_homogeneous = True

        for row in rows:
            for col in cols:
                module = self.layout.get_module(row, col)
                if module is None:
                    continue

                # Check parity filter
                if self._selected_parity is not None and (row + col) % 2 != self._selected_parity:
                    continue

                current_fan_rows = module.fan_grid_rows
                current_fan_cols = module.fan_grid_cols

                if fan_rows_per_module is None:
                    fan_rows_per_module = current_fan_rows
                    fan_cols_per_module = current_fan_cols
                elif fan_rows_per_module != current_fan_rows or fan_cols_per_module != current_fan_cols:
                    is_homogeneous = False

        # Default to 1x1 if no modules found
        fan_rows_per_module = fan_rows_per_module or 1
        fan_cols_per_module = fan_cols_per_module or 1

        total_fan_rows = len(rows) * fan_rows_per_module
        total_fan_cols = len(cols) * fan_cols_per_module

        return (total_fan_rows, total_fan_cols, fan_rows_per_module, fan_cols_per_module, is_homogeneous)

    def _detect_pattern_level(
        self,
        percent: float | list[float] | list[list[float]],
        nb_rows: int,
        nb_columns: int,
        fan_grid_rows: int,
        fan_grid_cols: int,
    ) -> str:
        """
        Detect whether the input should be applied at module-level or fan-level.

        Returns:
            'module' or 'fan'

        """
        # Scalar - always module level
        if isinstance(percent, (int, float)):
            return "module"

        # 2D matrix
        if len(percent) > 0 and isinstance(percent[0], list):
            matrix_rows = len(percent)
            matrix_cols = len(percent[0]) if percent[0] else 0

            # If input exceeds module dimensions, it must be fan-level intent
            # (e.g., 5 cols for 2 modules means fan-level, not module-level)
            cols_exceed_modules = matrix_cols > nb_columns and fan_grid_cols != nb_columns
            rows_exceed_modules = matrix_rows > nb_rows and fan_grid_rows != nb_rows

            if cols_exceed_modules or rows_exceed_modules:
                return "fan"

            # Default to module-level
            return "module"

        # 1D list - if length exceeds module count, treat as fan-level
        values_1d: list[float] = percent  # type: ignore[assignment]
        list_len = len(values_1d)

        # If list is longer than module columns (horizontal), use fan-level
        if list_len > nb_columns and fan_grid_cols != nb_columns:
            return "fan"

        # If list is longer than module rows (vertical context), use fan-level
        if list_len > nb_rows and fan_grid_rows != nb_rows:
            return "fan"

        # Default to module-level
        return "module"

    def _normalize_to_fan_matrix(
        self,
        percent: float | list[float] | list[list[float]],
        fan_grid_rows: int,
        fan_grid_cols: int,
    ) -> list[list[float]]:
        """Normalize input to a fan-level matrix."""
        # Handle scalar value
        if isinstance(percent, (int, float)):
            capped_value = max(0.0, min(100.0, float(percent)))
            return [[capped_value] * fan_grid_cols for _ in range(fan_grid_rows)]

        # Handle 2D matrix
        if len(percent) > 0 and isinstance(percent[0], list):
            matrix_2d: list[list[float]] = percent  # type: ignore[assignment]

            # Spread rows if needed
            if len(matrix_2d) < fan_grid_rows:
                matrix_2d = self._spread_rows(matrix_2d, fan_grid_rows)
            elif len(matrix_2d) > fan_grid_rows:
                matrix_2d = matrix_2d[:fan_grid_rows]

            # Spread columns for each row
            result: list[list[float]] = []
            for row_vals in matrix_2d:
                spread_cols = self._spread_values(list(row_vals), fan_grid_cols)
                capped_cols = [max(0.0, min(100.0, val)) for val in spread_cols]
                result.append(capped_cols)
            return result

        # Handle 1D list - spread based on selection context
        values_1d: list[float] = percent  # type: ignore[assignment]
        if self._selected_cols is not None and self._selected_rows is None:
            # Vertical spread
            spread_vertical = self._spread_values(values_1d, fan_grid_rows)
            capped_vertical = [max(0.0, min(100.0, val)) for val in spread_vertical]
            return [[val] * fan_grid_cols for val in capped_vertical]

        # Default: horizontal spread
        spread_horizontal = self._spread_values(values_1d, fan_grid_cols)
        capped_horizontal = [max(0.0, min(100.0, val)) for val in spread_horizontal]
        return [capped_horizontal[:] for _ in range(fan_grid_rows)]

    def _spread_rows(self, matrix: list[list[float]], target_rows: int) -> list[list[float]]:
        """Spread/repeat rows to match target row count."""
        if len(matrix) == 0:
            return [[0.0] for _ in range(target_rows)]
        if len(matrix) == 1:
            return [matrix[0][:] for _ in range(target_rows)]
        if len(matrix) >= target_rows:
            return matrix[:target_rows]

        repeat_factor = target_rows // len(matrix)
        remainder = target_rows % len(matrix)
        expanded: list[list[float]] = []
        for i, row in enumerate(matrix):
            count = repeat_factor + (1 if i < remainder else 0)
            expanded.extend([row[:] for _ in range(count)])
        return expanded

    def _apply_fan_level_matrix(
        self,
        fan_matrix: list[list[float]],
        rows: list[int],
        cols: list[int],
        fan_rows_per_module: int,
        fan_cols_per_module: int,
    ) -> None:
        """
        Apply a fan-level matrix to the selected modules.

        The fan_matrix dimensions should be:
        (len(rows) * fan_rows_per_module) x (len(cols) * fan_cols_per_module)

        """
        for row_idx, row in enumerate(rows):
            for col_idx, col in enumerate(cols):
                module = self.layout.get_module(row, col)
                if module is None:
                    continue

                # Check parity filter
                if self._selected_parity is not None and (row + col) % 2 != self._selected_parity:
                    continue

                layers = self._resolve_layers(module)

                # Calculate the starting position in the fan matrix for this module
                fan_row_start = row_idx * fan_rows_per_module
                fan_col_start = col_idx * fan_cols_per_module

                # Extract the sub-matrix for this module and apply to fans
                for local_fan_row in range(fan_rows_per_module):
                    for local_fan_col in range(fan_cols_per_module):
                        # Calculate fan index from grid position
                        fan_idx = local_fan_row * fan_cols_per_module + local_fan_col

                        # Skip if this fan is not in the selected fans
                        if self._selected_fans is not None and fan_idx not in self._selected_fans:
                            continue

                        # Skip if fan_idx exceeds module's actual fan count
                        if fan_idx >= module.fans_per_layer:
                            continue

                        # Get value from fan matrix
                        matrix_row = fan_row_start + local_fan_row
                        matrix_col = fan_col_start + local_fan_col

                        if matrix_row < len(fan_matrix) and matrix_col < len(fan_matrix[matrix_row]):
                            pwm_value = max(0.0, min(100.0, fan_matrix[matrix_row][matrix_col]))
                        else:
                            pwm_value = 0.0

                        for layer in layers:
                            self.layout.set_fan_pwm(row, col, layer, fan_idx, pwm_value)

    def _normalize_to_matrix(
        self,
        percent: float | list[float] | list[list[float]],
        nb_rows: int,
        nb_columns: int,
    ) -> list[list[float]]:
        # ! Handle scalar value
        if isinstance(percent, (int, float)):
            capped_value = max(0.0, min(100.0, float(percent)))
            return [[capped_value] * nb_columns for _ in range(nb_rows)]

        # ! Handle 2D matrix
        if len(percent) > 0 and isinstance(percent[0], list):
            matrix_2d: float | list[float] | list[list[float]] = percent  # type: ignore[assignment]
            # Spread rows to match nb_rows
            spread_row_count = len(matrix_2d)
            if spread_row_count != nb_rows:
                # We need to spread/repeat rows
                if spread_row_count == 0:
                    matrix_2d = [[0.0] * nb_columns for _ in range(nb_rows)]
                elif spread_row_count == 1:
                    matrix_2d = [matrix_2d[0][:] for _ in range(nb_rows)]
                elif spread_row_count < nb_rows:
                    repeat_factor = nb_rows // spread_row_count
                    remainder = nb_rows % spread_row_count
                    expanded: list[list[float]] = []
                    for i, row in enumerate(matrix_2d):
                        count = repeat_factor + (1 if i < remainder else 0)
                        expanded.extend([row[:] for _ in range(count)])
                    matrix_2d = expanded
                else:
                    matrix_2d = matrix_2d[:nb_rows]

            # Now spread columns for each row
            result: list[list[float]] = []
            for row_vals in matrix_2d:
                spread_cols = self._spread_values(row_vals, nb_columns)
                capped_cols = [max(0.0, min(100.0, val)) for val in spread_cols]
                result.append(capped_cols)
            return result

        # ! Handle 1D list
        values_1d: list[float] = percent  # type: ignore[assignment]
        if self._selected_rows is not None and self._selected_cols is None:
            spread_horizontal = self._spread_values(values_1d, nb_columns)
            capped_horizontal = [max(0.0, min(100.0, val)) for val in spread_horizontal]
            return [capped_horizontal[:] for _ in range(nb_rows)]
        if self._selected_cols is not None and self._selected_rows is None:
            spread_vertical = self._spread_values(values_1d, nb_rows)
            capped_vertical = [max(0.0, min(100.0, val)) for val in spread_vertical]
            return [[val] * nb_columns for val in capped_vertical]
        spread_horizontal = self._spread_values(values_1d, nb_columns)
        capped_horizontal = [max(0.0, min(100.0, val)) for val in spread_horizontal]
        return [capped_horizontal[:] for _ in range(nb_rows)]

    def _spread_values(self, values: list[float], target_size: int) -> list[float]:
        if len(values) == 0:
            return [0.0] * target_size
        if len(values) == 1:
            return [values[0]] * target_size
        if len(values) >= target_size:
            return values[:target_size]

        repeat_factor = target_size // len(values)
        remainder = target_size % len(values)

        result: list[float] = []
        for i, val in enumerate(values):
            count = repeat_factor + (1 if i < remainder else 0)
            result.extend([val] * count)

        return result
