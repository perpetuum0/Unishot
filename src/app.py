from PySide6.QtGui import QIcon, QAction
from PySide6.QtWidgets import QApplication, QSystemTrayIcon, QMenu

from screenshot import Screenshooter

app = QApplication([])
app.setQuitOnLastWindowClosed(False)

icon = QIcon("../images/icon.png")

tray = QSystemTrayIcon()
tray.setIcon(icon)
tray.setVisible(True)

menu = QMenu()
action = QAction("Options")
menu.addAction(action)

quit_ = QAction("Quit")
quit_.triggered.connect(app.quit)
menu.addAction(quit_)


shooter = Screenshooter()


def trayActivated(activationReason: QSystemTrayIcon) -> None:
    if (activationReason == QSystemTrayIcon.ActivationReason.Trigger):
        shooter.activate()


tray.activated.connect(trayActivated)
tray.setContextMenu(menu)
