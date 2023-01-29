
from PySide6.QtGui import QIcon, QAction
from PySide6.QtWidgets import QApplication, QSystemTrayIcon, QMenu

from screenShooter import ScreenShooter

app = QApplication([])
app.setQuitOnLastWindowClosed(False)

icon = QIcon("./images/icon.png")

tray = QSystemTrayIcon()
tray.setIcon(icon)
tray.setVisible(True)

menu = QMenu()
action = QAction("Options")
menu.addAction(action)

quit = QAction("Quit")
quit.triggered.connect(app.quit)
menu.addAction(quit)


shooter = ScreenShooter()


def trayActivated(activationReason: QSystemTrayIcon) -> None:
    if (activationReason == QSystemTrayIcon.ActivationReason.Trigger):
        shooter.activate()


tray.activated.connect(trayActivated)
tray.setContextMenu(menu)
