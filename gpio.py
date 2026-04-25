import RPi.GPIO as GPIO
import multiprocessing as mp
import time
import os

PIN = 3

process = None
running = False

def worker():
    print(f"Worker process started (PID: {os.getpid()})")
    while True:
        print("Doing heavy stuff...")
        time.sleep(1)

def toggle(channel):
    global process, running

    if not running:
        print("START (spawning process)")
        process = mp.Process(target=worker)
        process.start()
        running = True
    else:
        print("STOP (terminating process NOW)")
        process.terminate()   # 💀 instant kill
        process.join()
        running = False

# Setup
GPIO.setmode(GPIO.BCM)
GPIO.setup(PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

GPIO.add_event_detect(PIN, GPIO.FALLING, callback=toggle, bouncetime=300)

print("Ready. Press signal to toggle.")

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    pass
finally:
    if process is not None and process.is_alive():
        process.terminate()
        process.join()
    GPIO.cleanup()