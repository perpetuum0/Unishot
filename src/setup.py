from distutils.core import setup, Extension

module1 = Extension('tray',
                    sources=['tray/traymodule.c'],
                    include_dirs=[
                    ],
                    libraries=['shell32', 'user32'],
                    language="c"
                    )

setup(name='tray',
      version='1.0',
      description='This is a demo package',
      ext_modules=[module1])
