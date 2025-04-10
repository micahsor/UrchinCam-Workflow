import time
from datetime import datetime, timedelta
import subprocess

# Start camera recording for given duration in seconds
def start_camera_recording(duration_secs):
    current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    output_file = f"video_{current_time}.h264"
    
    command = [
        "rpicam-vid",
        "-t", str(duration_secs * 1000),
        "-o", output_file,
        "--inline",
        "--nopreview",
        "--annotate", "%Y-%m-%d_%H-%M-%S",
        "--annotate-text-size", "24",
        "--annotate-text-colour", "0xFFFFF",
        "--annotate-bg-colour", "0x00000"
    ]

    print(f"[{datetime.now().strftime('%H:%M:%S')}] Recording for {duration_secs} seconds → {output_file}")
    subprocess.run(command, check=True)

# Calculate seconds until next hour or half-hour
def seconds_until_next_slot(current_time):
    minute = current_time.minute
    second = current_time.second

    if minute < 30:
        next_slot = current_time.replace(minute=30, second=0, microsecond=0)
    else:
        next_slot = (current_time + timedelta(hours=1)).replace(minute=0, second=0, microsecond=0)

    delta = (next_slot - current_time).total_seconds()
    return int(delta)

# Main loop
def continuous_half_hour_segments():
    first_run = True

    while True:
        now = datetime.now ()

        if first_run:
            duration = seconds_until_next_slot(now)
            print("First run — recording until next half-hour or hour.")
            start_camera_recording(duration)
            first_run = False
            continue

        # Align with :00 or :30 exactly
        if now.minute in [0, 30]:  # No seconds indicated to provide one-minute buffer.
            start_camera_recording(1800)  # 30 minutes
            time.sleep(1800)
        else:
            time.sleep(5)  # Check again shortly

# Start the scheduler
continuous_half_hour_segments()