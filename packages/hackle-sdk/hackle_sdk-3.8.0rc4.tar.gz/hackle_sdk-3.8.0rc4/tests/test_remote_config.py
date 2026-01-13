from unittest.mock import Mock

from hackle.internal.hackle_core import HackleCore
from hackle.internal.user.hackle_user_resolver import HackleUserResolver
from hackle.internal.user.internal_hackle_user import InternalHackleUser
from hackle.model import User
from hackle.remote_config import HackleRemoteConfigImpl
from tests import base


class TestHackleRemoteConfiguration(base.BaseTest):
    def setUp(self):
        self.core = Mock(spec=HackleCore)
        self.user = Mock(spec=User)
        self.hackle_user = Mock(spec=InternalHackleUser)
        self.hackle_user_resolver = Mock(spec=HackleUserResolver)
        self.hackle_user_resolver.resolve_or_none.return_value = self.hackle_user
        self.remote_config = HackleRemoteConfigImpl(
            user=self.user,
            core=self.core,
            hackle_user_resolver=self.hackle_user_resolver
        )

    def test_default_value_가_적절하지_않은_type_인_경우_required_type_이_None_으로_호출됨(self):
        self.remote_config.get('key', [])
        self.core.remote_config.assert_called_once_with('key', self.hackle_user, 'UNKNOWN', [])

    def test_default_value_가_None_인_경우_required_type_이_None_으로_호출됨(self):
        self.remote_config.get('key', None)
        self.core.remote_config.assert_called_once_with('key', self.hackle_user, 'NULL', None)

    def test_key가_None_인_경우_internal_client_호출하지_않음(self):
        self.remote_config.get(None, None)
        self.core.remote_config.assert_not_called()

    def test_default_value_가_STRING_타입인_경우_required_type_이_STRING_으로_호출됨(self):
        self.remote_config.get('key', 'string value')
        self.core.remote_config.assert_called_once_with('key', self.hackle_user, 'STRING', 'string value')

    def test_default_value_가_int_타입인_경우_required_type_이_NUMBER_으로_호출됨(self):
        self.remote_config.get('key', 42)
        self.core.remote_config.assert_called_once_with('key', self.hackle_user, 'NUMBER', 42)

    def test_default_value_가_float_타입인_경우_required_type_이_NUMBER_으로_호출됨(self):
        self.remote_config.get('key', 42.412412421)
        self.core.remote_config.assert_called_once_with('key', self.hackle_user, 'NUMBER', 42.412412421)

    def test_default_value_가_bool_타입인_경우_required_type_이_BOOLEAN_으로_호출됨(self):
        self.remote_config.get('key', False)
        self.core.remote_config.assert_called_once_with('key', self.hackle_user, 'BOOLEAN', False)
