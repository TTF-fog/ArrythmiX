import asyncio
import random
import time
from collections import deque
from bleak import BleakClient
import rerun as rr
import numpy as np
from scipy.signal import butter, sosfilt
rr.init("rerun_example_fixed_window_plot")
import neurokit2
BATTERY_SERVICE_UUID = "0000180f-0000-1000-8000-00805f9b34fb"
BATTERY_CHARACTERISTIC_UUID = "0000abcd-0000-1000-8000-00805f9b34fb"
rr.connect_grpc("rerun+http://127.0.0.1:9876/proxy")

n1 = "# Device Metrics "
rr.log("device_data_desc", rr.TextDocument(n1, media_type=rr.MediaType.MARKDOWN), static=True)
n1 = "# Health Metrics"
rr.log("device_health_desc", rr.TextDocument(n1, media_type=rr.MediaType.MARKDOWN), static=True)
DEVICE_NAME = "blehr_sensor_1.0"
HEART_RATE_MEASUREMENT_UUID = "E2FD985E-CEB8-4CCB-9CD3-52563E4B5C62"
timestamps = []
hrs = deque(maxlen=10)
i = 0
async def get_prediction():
    while True:
        try:
              rr.log("predictions", rr.TextLog("Low Risk >24H", level=rr.TextLogLevel.INFO))
        except Exception as e:
            pass
        await asyncio.sleep(15)
async def notification_handler(sender, data):
    global i, hrs, timestamps, zi
    print(int(data))
    heart_rate = int(data)

    print(f"Heart Rate: {heart_rate}")
    hrs.append(heart_rate)
    rr.set_time("ecg", timestamp=time.time())
    # rr.send_columns("ecg",indexes=[times],columns=rr.Scalars.columns(scalars=hrs))
    rr.log("ecg",rr.Scalars(heart_rate))


    await asyncio.sleep(0.25)
async def get_battery_level(client):
    while True:
        pass
        #     value = await client.read_gatt_char(BATTERY_CHARACTERISTIC_UUID)
        #     battery_level = int.from_bytes(value, byteorder='little') / 100
        #     rr.set_time("ecg", timestamp=time.time())
        #     rr.log("battery", rr.Scalars(battery_level))
        #     print(f"Battery Level: {battery_level}%")

        # except Exception as e:
        #     print(f"Error reading battery level: {e}")
        # await asyncio.sleep(15)  # Read every 15 seconds

async def main():

    print(f"Attempting to connect to {DEVICE_NAME}...")

    client = None
    try:
        async with BleakClient("EA:93:4E:D4:61:60", timeout=20.0) as client:
            if client.is_connected:
                print(f"Connected to {DEVICE_NAME}")

                print(f"Subscribing to notifications for UUID: {HEART_RATE_MEASUREMENT_UUID}")
                await client.start_notify(HEART_RATE_MEASUREMENT_UUID, notification_handler)
                pred_task = asyncio.create_task(get_prediction())
                battery_task = asyncio.create_task(get_battery_level(client))
                print("Receiving heart rate notifications. Press Ctrl+C to stop.")
                while True:
                    await asyncio.sleep(1)
            else:
                print(f"Failed to connect to {DEVICE_NAME}")

    except asyncio.CancelledError:
        print("Program was cancelled.")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        if client and client.is_connected:
            try:
                await client.stop_notify(HEART_RATE_MEASUREMENT_UUID)
            except Exception as e:
                print(f"Error stopping notifications: {e}")
        print("Disconnected.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Program interrupted by user.")


