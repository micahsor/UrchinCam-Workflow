#!/usr/bin/env python3
import time
from datetime import datetime, timedelta
import subprocess
import os
import signal
import sys

# Log file name
LOG_FILE = "urchin_log.txt"

# Graceful exit flag
should_exit = False

def log(message):
    timestamp = datetime.now().strftime ("%Y-%m-%d %H:%M:%S")
    formatted = f"[{timestamp}] {message}"
    print (formatted)
    with open (LOG_FILE, "a") as f:
        f.write (formatted + "\n")

def signal_handler (sig, frame):
    global should_exit
    print ("[!] Received interrupt signal. Preparing to exit gracefully...")
    log ("[!] Received interrupt signal. Preparing to exit gracefully...")
    should_exit = True

signal.signal (signal.SIGINT, signal_handler)

# Start camera recording for given duration in seconds
def start_camera_recording(duration_secs):
    current_time = datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
    h264_file = f"video_{current_time}.h264"
    mp4_file = f"video_{current_time}.mp4"

    print(f"[{datetime.now().strftime('%H:%M:%S')}] Recording for {duration_secs} seconds → {mp4_file}")
    log (f"Recording for {duration_secs} seconds → {mp4_file}")
   
    command = [
        "rpicam-vid",
        "-t", str(duration_secs * 1000),
        "-o", h264_file,
        "--inline",
        "--nopreview"
    ]

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
        log (f"ERROR: Failed to record video.")
        log (f"Command: {e.cmd}")
        log (f"Exit code: {e.returncode}")
        
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
def continuous_half_hour_segments(max_runtime_secs=72*3600): # Sets max runtime to 72 hours.    
    global should_exit
    first_run = True
    start_time = time.time ()

    while not should_exit:
        now = datetime.now ()

        # Check if runtime exceeded
        elapsed = time.time() - start_time
        if elapsed >= max_runtime_secs:
            print (f"[{now.strftime('%H:%M:%S')}] 72 hours reached - exiting.")
            log ("72 hours reached - exiting.")
            break

        # Determine duration for this segment 
        if first_run:
            duration = (seconds_until_next_slot(now) - 60) # Subtracts one minute from duration as buffer. 
            print(f"First run [{now.strftime('%H:%M:%S')}]  — recording until next half-hour or hour.")
            log ("First run — recording until next half-hour or hour.")
            
            start_camera_recording(duration)
            first_run = False
            continue
        else:
            # Run current time through duration calculation.
            duration = seconds_until_next_slot (now)
            start_camera_recording (duration)
        
# Start the scheduler
continuous_half_hour_segments()
