# import Pythoncom
import win32com.client
import os
from sys import executable
from PySide6.QtCore import QStandardPaths

global shortcutPath, startupFolder

startupFolder = QStandardPaths.writableLocation(
    QStandardPaths.StandardLocation.AppDataLocation
) + "/Microsoft/Windows/Start Menu/Programs/Startup"


if not os.path.exists(executable):
    executable = None

shortcutPath = os.path.join(startupFolder, 'Unishot.lnk')


def setStartup(enabled: bool):
    if enabled:
        enableLaunchOnStartup()
    else:
        disableLaunchOnStartup()


def enableLaunchOnStartup():
    shell = win32com.client.Dispatch("WScript.Shell")
    shortcut = shell.CreateShortCut(shortcutPath)
    shortcut.Targetpath = executable
    shortcut.save()
    del shell, shortcut


def disableLaunchOnStartup():
    try:
        os.remove(shortcutPath)
    except FileNotFoundError:
        pass


def isEnabled():
    return os.path.exists(shortcutPath)
