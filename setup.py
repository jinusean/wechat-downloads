"""
This is a setup.py script generated by py2applet

Usage:
    python setup.py py2app
"""
from setuptools import setup
from dotenv import load_dotenv
import os

load_dotenv()


setup(
    name=os.getenv('APP_NAME'),
    app=['main_prod.py'],
    data_files=[
        '.env',
        ('configs', ['configs/.default-settings.json']),
        ('images', ['images/icon.icns'])],
    options={
        'py2app': {
            'iconfile': 'images/icon.icns',
            'plist': {
                'LSBackgroundOnly': True,
                'CFBundleIdentifier': 'com.wechat_downloads',
            }
        }
    },
    setup_requires=['py2app'],
)
