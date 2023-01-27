
from PySide6.QtGui import QIcon, QAction
from PySide6.QtWidgets import QApplication, QSystemTrayIcon, QMenu

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


def screenshot(activationReason):
    if (activationReason == QSystemTrayIcon.ActivationReason.Trigger):
        return


tray.activated.connect(screenshot)

tray.setContextMenu(menu)
