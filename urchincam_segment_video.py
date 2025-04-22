#!/usr/bin/env python3
import time
from datetime import datetime, timedelta
import subprocess
import os

# Start camera recording for given duration in seconds
def start_camera_recording(duration_secs):
    current_time = datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
    h264_file = f"video_{current_time}.h264"
    mp4_file = f"video_{current_time}.mp4"
    
    command = [
        "rpicam-vid",
        "-t", str(duration_secs * 1000),
        "-o", h264_file,
        "--inline",
        "--nopreview"
    ]

    print(f"[{datetime.now().strftime('%H:%M:%S')}] Recording for {duration_secs} seconds → {mp4_file}")
    try:
        subprocess.run(command, check=True)
        
        # Convert to mp4.
        convert_command = [
            "ffmpeg", "-y",
            "-framerate", "30",
            "-i", h264_file,
            "-c", "copy",
            mp4_file
        ]
        subprocess.run (convert_command, check = True)
        os.remove (h264_file)
        
        
    except subprocess.CalledProcessError as e:
        print (f"[{datetime.now().strftime('%H:%M:%S')}] ERROR: Failed to record video.")
        print ("Command:", e.cmd)
        print ("Exit code:", e.returncode)
        
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
            duration = (seconds_until_next_slot(now) - 60) # Subtracts one minute from duration as buffer. 
            print("First run — recording until next half-hour or hour.")
            start_camera_recording(duration)
            first_run = False
            continue

        # Run current time through duration calculation.
        now = datetime.now ()
        duration = seconds_until_next_slot (now)
        start_camera_recording (duration)
        
# Start the scheduler
continuous_half_hour_segments()
