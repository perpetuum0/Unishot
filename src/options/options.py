from PySide6.QtWidgets import QWidget, QTabWidget, QBoxLayout, QCheckBox, QApplication
from PySide6.QtCore import QSettings

import options.startup as startup


class OptionsWindow(QTabWidget):
    settings: QSettings

    def __init__(self) -> None:
        super().__init__()
        self.settings = QSettings()

        self.generalTab = QWidget()
        generalLayout = QBoxLayout(
            QBoxLayout.Direction.TopToBottom, self.generalTab
        )

        launchOnStartup = QCheckBox("Launch on startup")
        launchOnStartup.setChecked(startup.isEnabled())
        launchOnStartup.stateChanged.connect(self.setStartup)

        generalLayout.addWidget(launchOnStartup)

        self.addTab(self.generalTab, "General")

    def setStartup(self, state: int):
        state = True if state == 2 else False
        startup.setStartup(state)


def create_instance(app: QApplication = None) -> QApplication:
    if not app:
        app = QApplication()
    options = OptionsWindow()
    options.show()
    # options.hidden.connect(app.quit)
    # app.setActiveWindow(options)
    return app.exec()
