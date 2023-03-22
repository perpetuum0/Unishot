import sys


def run_screenshot(queue):
    from PySide6.QtWidgets import QApplication
    app = QApplication()
    queue.get()  # Wait for queue call...
    import rc_icons
    from screenshot import create_instance
    sys.exit(create_instance(app))


def run_options():
    import options
    sys.exit(options.create_instance())


def init_screenshot(queue):
    process = Process(name="Unishot", target=run_screenshot,
                      args=[queue], daemon=True)
    process.start()
    return process


if __name__ == "__main__":
    from multiprocessing import Process, Queue
    import tray
    scr_queue = Queue()
    scr_proc = init_screenshot(scr_queue)
    opt_proc = Process()

    def screenshot():
        global scr_proc
        scr_queue.put(True)
        scr_proc = init_screenshot(scr_queue)

    def options():
        global opt_proc
        opt_proc = Process(target=run_options)
        opt_proc.start()

    def quit_():
        if opt_proc:
            opt_proc.terminate()
        if scr_proc:
            scr_proc.terminate()
        sys.exit(0)

    tray.create_tray(screenshot, options, quit_)
