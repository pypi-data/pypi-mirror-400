"""
Windsuite SDK main module.
"""

from __future__ import annotations

import asyncio
import math
import traceback
from collections.abc import Awaitable, Callable
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Protocol

import socketio  # type: ignore[import-untyped]
from loguru import logger

from ._models_internal import TrackingDataDict, dict_to_dataclass
from .fan_control import FanControlBuilder, MachineLayout
from .models import ModuleInfo, ModuleType, TrackedWindProbeData, TrackingData, Vec3, WindProbeData

logger.remove()


class CallbackWindtrackData(Protocol):
    """
    This represents a callback function called whenever new windtrack data is received.

    It will pass the received data for the user to use.

    Args:
        data (dict[str, TrackingData]): Dictionary mapping object names (str) to their tracking data (TrackingData)

    """

    def __call__(self, data: dict[str, TrackingData]) -> None: ...


class CallbackWindprobeData(Protocol):
    """
    This represents a callback function called whenever new windprobe data is received.

    It will pass the received data for the user to use.

    Args:
        data (WindProbeData): The windprobe data received

    """

    def __call__(self, data: WindProbeData) -> None: ...


class CallbackModuleUpdate(Protocol):
    """
    This represents a callback function called whenever new module update data is received.

    It will pass the received data for the user to use.

    Args:
        data (dict[tuple[int, int], ModuleInfo]): Dictionary mapping module positions (row, col) to their ModuleInfo

    """

    def __call__(self, data: dict[tuple[int, int], ModuleInfo]) -> None: ...


class WindsuiteSDK:
    def __init__(
        self,
        base_url: str,
        port_rest_api: int = 8000,
        sio_port: int = 8001,
        sio_port_rt: int = 8002,
    ) -> None:
        self.port_rest_api = port_rest_api
        self.sio_port = sio_port
        self.sio_port_rt = sio_port_rt

        self.rest_base_url = base_url.rstrip("/") + f":{self.port_rest_api}" + "/api"
        self.sio_base_url = base_url.rstrip("/") + f":{self.sio_port}"
        self.sio_rt_base_url = base_url.rstrip("/") + f":{self.sio_port_rt}"

        self.__callback_windprobe: CallbackWindprobeData | None = None
        self.__callback_windtrack: CallbackWindtrackData | None = None
        self.__callback_module_update: CallbackModuleUpdate | None = None

        self._executor = ThreadPoolExecutor(max_workers=2, thread_name_prefix="windsuite")
        self._stop_events: list[asyncio.Event] = []
        self._loops: list[asyncio.AbstractEventLoop] = []

        self.__sio: socketio.AsyncClient
        self.__sio_rt: socketio.AsyncClient

        self.current_layout = MachineLayout.from_api(self.rest_base_url)
        self.fan_controller = FanControlBuilder(self.current_layout)

    def __start_async_thread(
        self,
        async_routine: Callable[[asyncio.Event], Awaitable[None]],
        thread_name: str,
    ) -> None:
        """
        Helper to start an async routine in a background thread using ThreadPoolExecutor.

        Args:
            async_routine: The async coroutine function to run (receives a stop_event)
            thread_name: Name for the thread

        """

        def run_async() -> None:
            loop: asyncio.AbstractEventLoop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop=loop)
            stop_event = asyncio.Event()

            # Store the loop and event for cleanup
            self._loops.append(loop)
            self._stop_events.append(stop_event)

            try:
                loop.run_until_complete(async_routine(stop_event))
            finally:
                loop.close()

        self._executor.submit(run_async)

    def start_communication(self) -> None:
        """
        Called to start real-time communication with the Windsuite server

        ---

        When calling this:
        - Windprobe data will be received and passed to the registered windprobe callback
        - Windtrack data will be received and passed to the registered windtrack callback
        - Module updates will be received and passed to the registered module update callback
        - Facility updates (layout changes) will be handled automatically
        """
        self.__start_async_thread(self.__socketio_client_routine, "socketio_client_thread")
        self.__start_async_thread(self.__socketio_rt_client_routine, "socketio_rt_client_thread")

    def cleanup(self) -> None:
        """
        Stops all communication threads and disconnects from socketio servers.
        """
        logger.info("Starting cleanup...")

        for loop, stop_event in zip(self._loops, self._stop_events, strict=True):
            loop.call_soon_threadsafe(stop_event.set)

        logger.info("Shutting down thread pool...")
        self._executor.shutdown(wait=True, cancel_futures=False)

        logger.info("Cleanup complete.")

    def __replace_sentinel_with_nan(self, vec: Vec3) -> None:
        """Replace -999 sentinel values with nan in a Vec3."""
        if vec.x == -999:
            vec.x = math.nan
        if vec.y == -999:
            vec.y = math.nan
        if vec.z == -999:
            vec.z = math.nan

    async def __handle_probe_data(self, data: dict[str, Any]) -> None:
        """Handle incoming probe data."""
        try:
            tracked_probe_data = dict_to_dataclass(TrackedWindProbeData, data)

            # Replace -999 sentinel values with nan in wind velocity fields
            windprobe = tracked_probe_data.windprobe_data
            self.__replace_sentinel_with_nan(windprobe.wind_velocity_mps_probe_ref)
            self.__replace_sentinel_with_nan(windprobe.wind_velocity_mps_windshaper_ref)
            self.__replace_sentinel_with_nan(windprobe.wind_velocity_mps_windshaper_ref_corrected)

            if self.__callback_windprobe:
                self.__callback_windprobe(windprobe)
        except (KeyError, TypeError, ValueError) as e:
            logger.error(f"Error parsing probe data: {e}")
            logger.debug(f"Received data keys: {list(data.keys())}")

    async def __handle_tracking_data(self, data: dict[str, Any]) -> None:
        """Handle incoming tracking data."""
        try:
            windtrack_dict = dict_to_dataclass(TrackingDataDict, data)
            if self.__callback_windtrack:
                self.__callback_windtrack(windtrack_dict.data)
        except (KeyError, TypeError, ValueError) as e:
            logger.error(f"Error parsing tracking data: {e}")
            logger.debug(f"Received data keys: {list(data.keys())}")

    async def __handle_module_update(self, data: dict[str, Any]) -> None:
        """Handle incoming module update data."""
        try:
            modules_info: dict[tuple[int, int], ModuleInfo] = {}
            updated_modules = data.get("updated_modules", {})
            for mac, module_data in updated_modules.items():
                # Look up row/col from the layout using MAC address
                position = self.current_layout.get_module_by_mac(mac)
                if position is None:
                    logger.warning("Received update for unknown module MAC: {}", mac)
                    continue
                row, col = position

                pwms_data: dict[str, list[float]] = module_data.get("pwms", {})
                rpms_data: dict[str, list[float]] = module_data.get("rpms", {})

                # Convert PWM values from 0-1000 range to 0-100 range
                target_pwm: list[list[float]] = [[value / 10.0 for value in pwms_data[key]] for key in sorted(pwms_data.keys())]
                if not target_pwm:
                    target_pwm = [[]]

                # Convert PWM values from 0-1000 range to 0-100 range
                current_pwm: list[list[float]] = [[value / 10.0 for value in pwms_data[key]] for key in sorted(pwms_data.keys())]
                if not current_pwm:
                    current_pwm = [[]]

                # Build current_rpm as list of lists (one inner list per layer)
                current_rpm: list[list[float]] = [rpms_data[key] for key in sorted(rpms_data.keys())]
                if not current_rpm:
                    current_rpm = [[]]

                module_type_str = module_data["type"]
                if module_type_str in {e.value for e in ModuleType}:
                    module_type_str = ModuleType(module_type_str).value
                else:
                    logger.warning("Unknown module type received: {}", module_type_str)

                module_info = ModuleInfo(
                    row=row,
                    col=col,
                    mac=module_data["mac"],
                    ip=module_data["ip"],
                    type=module_type_str,
                    lifepoints=module_data.get("lifepoints"),
                    target_pwm=target_pwm,
                    current_pwm=current_pwm,
                    current_rpm=current_rpm,
                    target_psu_state=bool(module_data.get("psu_command")),
                    current_psu_state=bool(module_data.get("is_psu")),
                    is_connected=bool(module_data.get("is_connected")),
                )
                modules_info[(row, col)] = module_info

            if self.__callback_module_update:
                self.__callback_module_update(modules_info)
            logger.debug("Parsed {} module(s): {}", len(modules_info), list(modules_info.keys()))
        except (KeyError, TypeError, ValueError) as e:
            logger.error(f"Error parsing module update data: {e} - {traceback.format_exc()}")
            logger.debug("Received data keys: {}", list(data.keys()))

    async def __handle_facility_update(self, data: dict[str, Any]) -> None:
        """Handle incoming facility update data (layout changes)."""
        try:
            windcontrol_layout = data.get("current_windcontrol_layout")
            if windcontrol_layout is None:
                logger.warning("Received facility_update without current_windcontrol_layout")
                return

            # Preserve the API URL from the current layout
            api_url = self.current_layout.api_url

            # Update the layout
            self.current_layout = MachineLayout.from_dict(windcontrol_layout, api_url=api_url)
            self.fan_controller = FanControlBuilder(self.current_layout)

            logger.info(
                f"Layout updated: {self.current_layout.nb_rows}x{self.current_layout.nb_columns} with {len(self.current_layout.modules)} modules"
            )
        except (KeyError, TypeError, ValueError) as e:
            logger.error(f"Error parsing facility update data: {e} - {traceback.format_exc()}")
            logger.debug("Received data keys: {}", list(data.keys()))

    async def __socketio_client_routine(self, stop_event: asyncio.Event) -> None:
        """
        Base socketio client for general events (windprobe data)
        """
        self.__sio: socketio.AsyncClient = socketio.AsyncClient(
            reconnection=False,
            request_timeout=5,
            reconnection_delay=1,
            reconnection_delay_max=5,
        )
        # ? Ignore rationales: sio is badly typed

        @self.__sio.event  # pyright: ignore[reportUnknownMemberType]
        async def connect() -> None:  # pyright: ignore[reportUnusedFunction]
            logger.info("Connected to SocketIO server.")

        @self.__sio.event  # pyright: ignore[reportUnknownMemberType]
        async def disconnect() -> None:  # pyright: ignore[reportUnusedFunction]
            logger.info("Disconnected from SocketIO server.")

        @self.__sio.event  # pyright: ignore[reportUnknownMemberType]
        async def probe_data(data: dict[str, Any]) -> None:  # pyright: ignore[reportUnusedFunction]
            await self.__handle_probe_data(data)

        @self.__sio.event  # pyright: ignore[reportUnknownMemberType]
        async def module_update(data: dict[str, Any]) -> None:  # pyright: ignore[reportUnusedFunction]
            await self.__handle_module_update(data)

        @self.__sio.event  # pyright: ignore[reportUnknownMemberType]
        async def facility_update(data: dict[str, Any]) -> None:  # pyright: ignore[reportUnusedFunction]
            await self.__handle_facility_update(data)

        try:
            await self.__sio.connect(  # pyright: ignore[reportUnknownMemberType]
                self.sio_base_url,
                transports=["websocket"],
                wait=True,
                wait_timeout=1,
            )
        except socketio.exceptions.ConnectionError as err:  # type: ignore[UnknownMemberType], Rationale : type hints of socketio are not strict enough
            logger.error(
                f"Socket IO connection error: {err}\nHINT:\n\t- Verify that the server is running\n\t- The URL is correct\n\t- You're on the same network as the server"
            )
            return

        await stop_event.wait()

        logger.info("Shutting down SIO client...")
        await self.__sio.disconnect()  # pyright: ignore[reportUnknownMemberType]
        logger.info("SIO client disconnected.")

    async def __socketio_rt_client_routine(self, stop_event: asyncio.Event) -> None:
        """
        Real-time socketio client
        """
        self.__sio_rt: socketio.AsyncClient = socketio.AsyncClient(
            reconnection=False,
            request_timeout=5,
            reconnection_delay=1,
            reconnection_delay_max=5,
        )
        # ? Ignore rationales: sio is badly typed

        @self.__sio_rt.event  # pyright: ignore[reportUnknownMemberType]
        async def connect() -> None:  # pyright: ignore[reportUnusedFunction]
            logger.info("Connected to SocketIO RT server.")

        @self.__sio_rt.event  # pyright: ignore[reportUnknownMemberType]
        async def disconnect() -> None:  # pyright: ignore[reportUnusedFunction]
            logger.info("Disconnected from SocketIO RT server.")

        @self.__sio_rt.event  # pyright: ignore[reportUnknownMemberType]
        async def tracking_data(data: dict[str, Any]) -> None:  # pyright: ignore[reportUnusedFunction]
            await self.__handle_tracking_data(data)

        try:
            await self.__sio_rt.connect(  # pyright: ignore[reportUnknownMemberType]
                self.sio_rt_base_url,
                transports=["websocket"],
                wait=True,
                wait_timeout=1,
            )
        except socketio.exceptions.ConnectionError as err:  # type: ignore[UnknownMemberType], Rationale : type hints of socketio are not strict enough
            logger.error(
                f"Socket IO RT connection error: {err}\nHINT:\n\t- Verify that the server is running\n\t- The URL is correct\n\t- You're on the same network as the server"
            )
            return

        await stop_event.wait()

        logger.info("Shutting down SIO RT client...")
        await self.__sio_rt.disconnect()  # pyright: ignore[reportUnknownMemberType]
        logger.info("SIO RT client disconnected.")

    def register_tracking_callback(
        self,
        callback: CallbackWindtrackData,
    ) -> None:
        """
        Register a callback for windtrack data.

        Args:
            callback (CallbackWindtrackData): The function to call when windtrack data is received.
                                         Receives a dict mapping object names to TrackingData.

        """
        if not callable(callback):
            raise TypeError("Callback must be a callable function.")

        self.__callback_windtrack = callback

    def register_windprobe_callback(
        self,
        callback: CallbackWindprobeData,
    ) -> None:
        """
        Register a callback for windprobe data.

        Args:
            callback (CallbackWindprobeData): The function to call when windprobe data is received.

        """
        if not callable(callback):
            raise TypeError("Callback must be a callable function.")

        self.__callback_windprobe = callback

    def register_module_update_callback(
        self,
        callback: CallbackModuleUpdate,
    ) -> None:
        """
        Register a callback for module update data.

        Args:
            callback (CallbackModuleUpdate): The function to call when module update data is received.

        """
        if not callable(callback):
            raise TypeError("Callback must be a callable function.")

        self.__callback_module_update = callback
