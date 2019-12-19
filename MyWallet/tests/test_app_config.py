from django.test import TestCase

from MyWallet.apps import SilverStrikeConfig


class AppConfigTest(TestCase):
    def test(self):
        self.assertEqual(SilverStrikeConfig.name, 'MyWallet')
