import RPi.GPIO as GPIO
import threading
import time
import actions

PIN = 3

# Thread control
worker_thread = None
stop_event = threading.Event()

def worker():
    print("Worker thread started")
    while not stop_event.is_set():
        print("Running task...")
        time.sleep(1)
    print("Worker thread stopping")

def toggle_thread(channel):
    global worker_thread, stop_event

    if worker_thread is None or not worker_thread.is_alive():
        print("Starting thread")
        stop_event.clear()
        worker_thread = threading.Thread(target=worker)
        worker_thread.start()
    else:
        print("Stopping thread")
        stop_event.set()
        worker_thread.join()
        worker_thread = None

# Setup
GPIO.setmode(GPIO.BCM)
GPIO.setup(PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Detect FALLING edge (HIGH -> LOW when connected to GND)
GPIO.add_event_detect(PIN, GPIO.FALLING, callback=toggle_thread, bouncetime=300)

print("Listening on GPIO3... (Ctrl+C to exit)")

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("Cleaning up...")
finally:
    GPIO.cleanup()