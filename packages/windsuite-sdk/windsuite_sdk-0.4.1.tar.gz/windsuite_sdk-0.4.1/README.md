# WindShape Software Suite SDK

## Installation

```bash
uv add windsuite_sdk

# Legacy pip method
pip install windsuite_sdk
```


## Basic Example

```python
from windsuite_sdk import WindsuiteSDK
sdk = WindsuiteSDK(base_url="http://localhost")
sdk.start_communication()

# Set all fans to 75% intensity
sdk.fan_controller.set_intensity(percent=75).apply()
```

## Advanced Examples

Fan controller - Checkerboard Pattern:
```python
from windsuite_sdk import WindsuiteSDK

sdk = WindsuiteSDK(base_url="http://localhost")
sdk.start_communication()

sdk.fan_controller.fans(fans=[1, 3, 5, 7, 9]).even_modules().set_intensity(
    percent=[[30]]
)

sdk.fan_controller.fans(fans=[2, 4, 6, 8]).odd_modules().set_intensity(
    percent=[[100]]
)

sdk.fan_controller.apply()
```


Complete example
```python
import os
import threading

from dotenv import load_dotenv
from windsuite_sdk import ModuleInfo, TrackingData, WindProbeData, WindsuiteSDK

load_dotenv()

SERVER_IP_ADDRESS = os.getenv("SERVER_IP_ADDRESS", default="localhost")


def on_windprobe_data(data: WindProbeData) -> None:
    """
    Callback for wind probe data.

    Args:
        data: Wind probe measurements including velocity, temperature, and pressure.

    """
    print("=== Wind Probe Data ===")
    print(f"Timestamp: {data.timestamp_s}s")
    print(
        f"Wind Velocity (probe ref): ({data.wind_velocity_mps_probe_ref.x:.2f}, "
        f"{data.wind_velocity_mps_probe_ref.y:.2f}, "
        f"{data.wind_velocity_mps_probe_ref.z:.2f}) m/s"
    )
    print(
        f"Wind Velocity (windshaper ref): ({data.wind_velocity_mps_windshaper_ref.x:.2f}, "
        f"{data.wind_velocity_mps_windshaper_ref.y:.2f}, "
        f"{data.wind_velocity_mps_windshaper_ref.z:.2f}) m/s"
    )
    print(f"Temperature: {data.temperature_celcius:.2f}°C")
    print(f"Atmospheric Pressure: {data.atmospheric_pressure_hpascal:.2f} hPa")
    print(f"Static Pressure: {data.static_pressure_pascal:.2f} Pa")
    print()


def on_tracking_data(data: dict[str, TrackingData]) -> None:
    """
    Callback for tracking data.

    Args:
        data: Dictionary mapping object names to their tracking data.

    """
    print(f"=== Tracking Data ({len(data)} objects) ===")

    for object_name, tracking_data in data.items():
        print(f"Object: {object_name}")
        print(f"  Timestamp: {tracking_data.timestamp}s")

        # Position
        pos = tracking_data.position_meters_world_ref
        print(f"  Position (world): ({pos.x:.3f}, {pos.y:.3f}, {pos.z:.3f}) m")

        # Rotation (quaternion)
        rot = tracking_data.rotation_world_ref
        print(
            f"  Rotation (world): w={rot.w:.3f}, x={rot.x:.3f}, y={rot.y:.3f}, z={rot.z:.3f}"
        )

        vel = tracking_data.velocity_mps_world_ref
        norm = (vel.x**2 + vel.y**2 + vel.z**2) ** 0.5
        print(
            f"  Velocity (world): (X:{vel.x:.2f}, Y:{vel.y:.2f}, Z:{vel.z:.2f}) m/s | Norm : {norm:.2f} m/s"
        )

    print()


def on_module_update(data: dict[tuple[int, int], ModuleInfo]) -> None:
    """
    Callback for module updates.

    Args:
        data: Dictionary mapping module row and column to their information.


    """

    for position, module_info in data.items():
        print(f"Module Position: {position}")
        print(f"  IP Address: {module_info.ip}")
        print(f"  Type: {module_info.type}")
        print(f"  Lifepoints: {module_info.lifepoints}")

        # ! FOR EACH FAN LAYER
        # The fans are indexed as a 3x3 matrix as they are physically arranged in the modules
        # ┌─────┬─────┬─────┐
        # │  1  │  2  │  3  │
        # ├─────┼─────┼─────┤
        # │  4  │  5  │  6  │
        # ├─────┼─────┼─────┤
        # │  7  │  8  │  9  │
        # └─────┴─────┴─────┘

        for layer_index in range(len(module_info.target_pwm)):
            layer_name = (
                "DOWNSTREAM"
                if layer_index == ModuleInfo.INDEX_DOWNSTREAM
                else "UPSTREAM"
            )
            print(f"\tLayer {layer_name}:")

            # ! FOR EACH FAN IN THE LAYER
            for fan_index in range(len(module_info.target_pwm[layer_index])):
                target_pwm = module_info.target_pwm[layer_index][fan_index]
                current_pwm = module_info.current_pwm[layer_index][fan_index]
                current_rpm = module_info.current_rpm[layer_index][fan_index]

                print(
                    f"\t\tFan {fan_index}: Target PWM: {target_pwm:.2f} | Current PWM: {current_pwm:.2f} | Current RPM: {current_rpm:.2f}"
                )

    print("-" * 20)


stop_event = threading.Event()


def main() -> None:
    base_url = f"http://{SERVER_IP_ADDRESS}"
    print(f"Connecting to WindSuite server at {base_url}")

    sdk = WindsuiteSDK(base_url=base_url)

    sdk.register_windprobe_callback(callback=on_windprobe_data)
    sdk.register_tracking_callback(callback=on_tracking_data)
    sdk.register_module_update_callback(callback=on_module_update)

    sdk.start_communication()

    try:
        freq_hz = 25
        sinus_freq_hz = 2

        while not stop_event.wait(timeout=(1.0 / freq_hz)):

            # ! SINUS MODULE CHECKERBOARD EXAMPLE
            intensity = 50 + 50 * math.sin(2 * math.pi * sinus_freq_hz * time.time())
            sdk.fan_controller.even_modules().set_intensity(percent=intensity)

    except KeyboardInterrupt:
        print("\nShutting down...")
        stop_event.set()
    finally:
        sdk.fan_controller.set_intensity(0).apply()

        sdk.cleanup()
        print("SDK stopped")


if __name__ == "__main__":
    main()


