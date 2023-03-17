from distutils.core import setup, Extension

traymod = Extension('tray',
                    sources=['traymodule.c'],
                    libraries=['shell32', 'user32'])

setup(name='tray',
      ext_modules=[traymod])
