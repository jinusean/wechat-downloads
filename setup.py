"""
This is a setup.py script generated by py2applet

Usage:
    python setup.py py2app
"""

from setuptools import setup

APP = ['Watch WeChat Files.py']
DATA_FILES = ['config.json']
OPTIONS = dict(
    iconfile='images/icon.icns',
    plist=dict(
        LSBackgroundOnly=True,
        CFBundleIdentifier='com.jameslee.watch_wechat_files',
    )
)

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
