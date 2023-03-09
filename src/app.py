from PySide6.QtGui import QIcon, QAction
from PySide6.QtWidgets import QApplication, QSystemTrayIcon, QMenu
from PySide6.QtCore import Signal, QObject, QThread
import global_hotkeys as hotkeys

from screenshot.shooter import Screenshooter
from options.options import OptionsWindow


class HotkeyListener(QObject):
    print_screen = Signal()

    def run(self):
        hotkeys.register_hotkey(
            "print_screen", [], self.print_screen.emit
        )
        hotkeys.start_checking_hotkeys()


class Unishot(QApplication):
    def __init__(self) -> None:
        super(Unishot, self).__init__()
        self.setQuitOnLastWindowClosed(False)
        self.setOrganizationName("Unishot")
        self.aboutToQuit.connect(self.quitEvent)

        self.shooter = Screenshooter()
        self.options = OptionsWindow()

        menu = QMenu()
        icon = QIcon(":/icons/tray")

        options_ = QAction("Options")
        options_.triggered.connect(self.options.show)
        menu.addAction(options_)

        quit_ = QAction("Quit")
        quit_.triggered.connect(self.quit)
        menu.addAction(quit_)

        self.tray = QSystemTrayIcon()
        self.tray.setIcon(icon)
        self.tray.setContextMenu(menu)
        self.tray.setVisible(True)
        self.tray.activated.connect(self.trayActivated)

        self.runHotkeyListener()
        self.exec()

    def runHotkeyListener(self) -> None:
        # Run HotkeyListener in a different thread to prevent freezing.
        self.hotkeyThread = QThread()

        self.hotkeyListener = HotkeyListener()

        self.hotkeyListener.moveToThread(self.hotkeyThread)
        self.hotkeyListener.print_screen.connect(self.screenshot)

        self.hotkeyThread.started.connect(self.hotkeyListener.run)
        self.hotkeyThread.start()

    def screenshot(self) -> None:
        if not self.shooter.active():
            self.shooter.activate()

    def trayActivated(self, activationReason: QSystemTrayIcon) -> None:
        if (activationReason == QSystemTrayIcon.ActivationReason.Trigger):
            self.screenshot()

    def quitEvent(self) -> None:
        self.hotkeyThread.quit()
