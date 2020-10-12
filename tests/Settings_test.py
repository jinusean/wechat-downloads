from unittest import TestCase
from src.Settings import Settings
from tests.mocks.WeChatDownloadsApp import WeChatDownloadsApp


class SettingsTest(TestCase):
    def setUp(self):
        self.settings = Settings(WeChatDownloadsApp())





