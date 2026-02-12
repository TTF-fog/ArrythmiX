import time
import asyncio
import rerun as rr
import neurokit2 as nk
import numpy as np

async def send_prediction():
    while True:
        rr.log(
            "prediction",
            rr.TextLog(
                level=rr.TextLogLevel.INFO,
                text="VFib: Low Risk, >24 Hours",
            ),
        )
        rr.log(
            "prediction",
            rr.TextLog(
                level=rr.TextLogLevel.INFO,
                text="Arrhythmia: Normal Beat",
            ),
        )
        await asyncio.sleep(15)


ti = np.array((-70, -15, 0, 15, 100))
ai = np.array((1.2, -5, 30, -7.5, 0.75))
bi = np.array((0.25, 0.1, 0.1, 0.1, 0.4))

ti = np.random.normal(ti, np.ones(5) * 3)
ai = np.random.normal(ai, np.abs(ai / 5))
bi = np.random.normal(bi, np.abs(bi / 5))

rr.init("dashboard", spawn=True)

good_ecg1 = nk.ecg_simulate(
    duration=150,
    noise=0.03,
    heart_rate=71,
    method="ecgsyn",
    random_state_distort="spawn",
    ti=ti,
    ai=ai,
    bi=bi,
)

# -----------------------------
# Main async loop
# -----------------------------
async def main():
    # start background task
    prediction_task = asyncio.create_task(send_prediction)

    try:
        for y in range(len(good_ecg1)):
            rr.set_time("ecg", timestamp=time.time())
            rr.log("ecg", rr.Scalars(good_ecg1[y]))

            await asyncio.sleep(0.01)

    finally:
        prediction_task.cancel()
        with contextlib.suppress(asyncio.CancelledError):
            await prediction_task


if __name__ == "__main__":
    asyncio.run(main())
