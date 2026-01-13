from hackle.config import HackleConfig, HackleConfigBuilder
from hackle.commons.enums import Default
from tests import base


class TestHackleConfig(base.BaseTest):

    def test_default(self):
        config = HackleConfig.default()
        self.assertEqual(config.sdk_url, Default.SDK_URL)
        self.assertEqual(config.event_url, Default.EVENT_URL)
        self.assertEqual(config.monitoring_url, Default.MONITORING_URL)

    def test_builder_with_all_values(self):
        config = HackleConfig.builder() \
            .sdk_url("https://custom-sdk.hackle.io") \
            .event_url("https://custom-event.hackle.io") \
            .monitoring_url("https://custom-monitoring.hackle.io") \
            .build()

        self.assertEqual(config.sdk_url, "https://custom-sdk.hackle.io")
        self.assertEqual(config.event_url, "https://custom-event.hackle.io")
        self.assertEqual(config.monitoring_url, "https://custom-monitoring.hackle.io")

    def test_builder_with_default_values(self):
        config = HackleConfig.builder().build()

        self.assertEqual(config.sdk_url, Default.SDK_URL)
        self.assertEqual(config.event_url, Default.EVENT_URL)
        self.assertEqual(config.monitoring_url, Default.MONITORING_URL)

    def test_builder_with_partial_values(self):
        config = HackleConfig.builder() \
            .sdk_url("https://custom-sdk.hackle.io") \
            .build()

        self.assertEqual(config.sdk_url, "https://custom-sdk.hackle.io")
        self.assertEqual(config.event_url, Default.EVENT_URL)
        self.assertEqual(config.monitoring_url, Default.MONITORING_URL)

    def test_builder_with_none_or_empty_values(self):
        config = HackleConfig.builder() \
            .sdk_url(None) \
            .event_url("") \
            .build()

        self.assertEqual(config.sdk_url, Default.SDK_URL)
        self.assertEqual(config.event_url, Default.EVENT_URL)
        self.assertEqual(config.monitoring_url, Default.MONITORING_URL)
