import time
import threading
import sys


def format_duration(seconds):
    minutes, seconds = divmod(int(seconds), 60)
    hours, minutes = divmod(minutes, 60)
    if hours:
        return f"{hours}h {minutes}m {seconds}s"
    elif minutes:
        return f"{minutes}m {seconds}s"
    else:
        return f"{seconds}s"


def timer_display(start, stop_event):
    while not stop_event.is_set():
        elapsed = time.time() - start
        sys.stdout.write(f"\r{format_duration(elapsed)}")
        sys.stdout.flush()
        time.sleep(1)


def timer_start(label):
    start = time.time()
    stop_event = threading.Event()
    thread = threading.Thread(target=timer_display, args=(start, stop_event), daemon=True)
    thread.start()

    try:
        input()
    except KeyboardInterrupt:
        print("\nCtrl+C Interrupt!")
    finally:
        stop_event.set()
        thread.join(timeout=0.1)

    end = time.time()
    duration = end - start
    return start, end, duration
