from .commons.enums import Default


class HackleConfig(object):
    """
    Configuration object for Hackle SDK.
    """

    def __init__(self, sdk_url, event_url, monitoring_url):
        """
        :param str sdk_url:
        :param str event_url:
        :param str monitoring_url:
        """
        self._sdk_url = sdk_url
        self._event_url = event_url
        self._monitoring_url = monitoring_url

    @property
    def sdk_url(self):
        """
        :rtype: str
        """
        return self._sdk_url

    @property
    def event_url(self):
        """
        :rtype: str
        """
        return self._event_url

    @property
    def monitoring_url(self):
        """
        :rtype: str
        """
        return self._monitoring_url

    @staticmethod
    def builder():
        """
        Creates a new HackleConfigBuilder instance.

        :rtype: HackleConfigBuilder
        """
        return HackleConfigBuilder()

    @staticmethod
    def default():
        """
        Creates a HackleConfig with default values.

        :rtype: HackleConfig
        """
        return HackleConfig(
            sdk_url=Default.SDK_URL,
            event_url=Default.EVENT_URL,
            monitoring_url=Default.MONITORING_URL
        )

    def __str__(self):
        return 'HackleConfig(sdk_url={}, event_url={}, monitoring_url={})'.format(self._sdk_url,
                                                                                  self._event_url,
                                                                                  self._monitoring_url)

    def __repr__(self):
        return self.__str__()


class HackleConfigBuilder(object):
    """
    Builder for HackleConfig.
    """

    def __init__(self):
        self._sdk_url = None
        self._event_url = None
        self._monitoring_url = None

    def sdk_url(self, url):
        """
        Sets the SDK URL. If empty or None, the default URL will be used.

        :param str url: SDK URL
        :rtype: HackleConfigBuilder
        """
        self._sdk_url = url
        return self

    def event_url(self, url):
        """
        Sets the event URL. If empty or None, the default URL will be used.

        :param str url: Event URL
        :rtype: HackleConfigBuilder
        """
        self._event_url = url
        return self

    def monitoring_url(self, url):
        """
        Sets the monitoring URL. If empty or None, the default URL will be used.

        :param str url: Monitoring URL
        :rtype: HackleConfigBuilder
        """
        self._monitoring_url = url
        return self

    def build(self):
        """
        Builds the HackleConfig instance.
        If any URL is empty or None, the default value will be used.

        :rtype: HackleConfig
        """
        return HackleConfig(
            sdk_url=self._sdk_url if self._sdk_url else Default.SDK_URL,
            event_url=self._event_url if self._event_url else Default.EVENT_URL,
            monitoring_url=self._monitoring_url if self._monitoring_url else Default.MONITORING_URL
        )
