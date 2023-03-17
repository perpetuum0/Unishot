from multiprocessing import Process, Queue
import sys


def run_screenshot(queue):
    import screenshot
    import screenshot.rc_icons
    from PySide6.QtWidgets import QApplication
    app = QApplication()
    queue.get()  # Wait for queue call...
    sys.exit(screenshot.create_instance(app))


def run_options():
    import options
    sys.exit(options.create_instance())


def init_screenshot(queue):
    process = Process(target=run_screenshot, args=[queue])
    process.start()
    return process


if __name__ == "__main__":
    import tray
    queue = Queue()
    proc = init_screenshot(queue)

    def screenshot():
        global proc
        queue.put(True)
        proc.join()
        proc = init_screenshot(queue)

    def options():
        process = Process(target=run_options)
        process.start()

    tray.create_tray(screenshot, options)
