from unittest import TestCase
from unittest.mock import Mock

from hackle import hackle
from hackle.decision import ExperimentDecision, DecisionReason, FeatureFlagDecision
from hackle.internal.hackle_core import HackleCore
from hackle.internal.user.internal_hackle_user import InternalHackleUser
from hackle.model import HackleUser, Hackle, HackleEvent, PropertyOperations
from hackle.remote_config import HackleRemoteConfigImpl


class HackleClientTest(TestCase):

    def setUp(self):
        self.core = Mock(spec=HackleCore)
        self.sut = hackle.Client('SDK_KEY')
        self.sut._core = self.core

    def test__variation_detail__when_experiment_key_is_invalid_then_returns_default_variation(self):
        user = HackleUser.builder().id('user').build()

        self.assertEqual(
            ExperimentDecision('A', DecisionReason.INVALID_INPUT),
            self.sut.variation_detail('42', user)
        )

        self.assertEqual(
            ExperimentDecision('A', DecisionReason.INVALID_INPUT),
            self.sut.variation_detail({'key': 42}, user)
        )

    def test__variation_detail__when_cannot_resolve_hackle_user_then_returns_default_variation(self):
        user = HackleUser.builder().build()

        actual = self.sut.variation_detail(42, user)

        self.assertEqual(ExperimentDecision('A', DecisionReason.INVALID_INPUT), actual)

    def test__variation_detail__when_exception_raised_then_returns_default_variation(self):
        # given
        user = HackleUser.builder().id("user").build()
        self.core.experiment.side_effect = Mock(side_effect=Exception('fail'))

        # when
        actual = self.sut.variation_detail(42, user)

        # then
        self.assertEqual(ExperimentDecision('A', DecisionReason.EXCEPTION), actual)

    def test___variation_detail__decision(self):
        # given
        user = HackleUser.builder().id("user").build()
        decision = ExperimentDecision('B', DecisionReason.TRAFFIC_ALLOCATED)
        self.core.experiment.return_value = decision

        # when
        actual = self.sut.variation_detail(42, user)

        # then
        self.assertEqual(decision, actual)

    def test___variation_detail_legacy_user(self):
        decision = ExperimentDecision('B', DecisionReason.TRAFFIC_ALLOCATED)
        self.core.experiment.return_value = decision

        self.assertEqual(decision, self.sut.variation_detail(42, Hackle.user(id='user')))
        self.assertEqual(decision, self.sut.variation_detail(42, HackleUser(id='user')))

    def test__variation(self):
        # given
        user = HackleUser.builder().id("user").build()
        decision = ExperimentDecision('B', DecisionReason.TRAFFIC_ALLOCATED)
        self.core.experiment.return_value = decision

        # when
        actual = self.sut.variation(42, user)

        # then
        self.assertEqual('B', actual)

    def test__feature_flag_detail__when_feature_key_is_invalid_then_returns_false(self):
        user = HackleUser.builder().id('user').build()

        self.assertEqual(
            FeatureFlagDecision(False, DecisionReason.INVALID_INPUT),
            self.sut.feature_flag_detail('42', user)
        )

        self.assertEqual(
            FeatureFlagDecision(False, DecisionReason.INVALID_INPUT),
            self.sut.feature_flag_detail({'key': 42}, user)
        )

    def test___feature_flag_detail__when_cannot_resolve_user_then_return_false(self):
        user = HackleUser.builder().build()

        actual = self.sut.feature_flag_detail(42, user)

        self.assertEqual(FeatureFlagDecision(False, DecisionReason.INVALID_INPUT), actual)

    def test___feature_flag_detail__when_exception_raised_then_returns_false(self):
        # given
        user = HackleUser.builder().id("user").build()
        self.core.feature_flag.side_effect = Mock(side_effect=Exception('fail'))

        # when
        actual = self.sut.feature_flag_detail(42, user)

        # then
        self.assertEqual(FeatureFlagDecision(False, DecisionReason.EXCEPTION), actual)

    def test__feature_flag_detail__decision(self):
        # given
        user = HackleUser.builder().id("user").build()
        decision = FeatureFlagDecision(True, DecisionReason.DEFAULT_RULE)
        self.core.feature_flag.return_value = decision

        # when
        actual = self.sut.feature_flag_detail(42, user)

        # then
        self.assertEqual(decision, actual)

    def test__feature_flag_detail_legacy_user(self):
        decision = FeatureFlagDecision(True, DecisionReason.DEFAULT_RULE)
        self.core.feature_flag.return_value = decision

        self.assertEqual(decision, self.sut.feature_flag_detail(42, Hackle.user(id='user')))
        self.assertEqual(decision, self.sut.feature_flag_detail(42, HackleUser(id='user')))

    def test__is_feature_on(self):
        # given
        user = HackleUser.builder().id("user").build()
        decision = FeatureFlagDecision(True, DecisionReason.DEFAULT_RULE)
        self.core.feature_flag.return_value = decision

        # when
        actual = self.sut.is_feature_on(42, user)

        # then
        self.assertTrue(actual)

    def test__track__when_event_is_invalid_then_do_not_track(self):
        user = HackleUser.builder().id("user").build()

        self.sut.track('test', user)
        self.sut.track(123, user)
        self.sut.track(True, user)
        self.sut.track({'key': 'a'}, user)

        self.core.track.assert_not_called()

    def test__track_when_cannot_resolve_user_then_do_not_track(self):
        event = HackleEvent.builder('test').build()
        self.sut.track(event, 'user')
        self.sut.track(event, {'id': 'user'})

        self.core.track.assert_not_called()

    def test__track(self):
        event = HackleEvent.builder('purchase') \
            .value(4200) \
            .property('discount_amount', 42) \
            .property('pay_method', 'CARD') \
            .property('is_discounted', True) \
            .build()

        user = HackleUser.builder() \
            .id('id') \
            .user_id('user_id') \
            .device_id('device_id') \
            .identifier('custom_id', 'custom') \
            .property('age', 42) \
            .property('grade', 'GOLD') \
            .property('membership', True) \
            .build()

        self.sut.track(event, user)

        args = self.core.track.call_args[0]

        self.assertEqual(
            HackleEvent(
                key='purchase',
                value=4200,
                properties={
                    'discount_amount': 42,
                    'pay_method': 'CARD',
                    'is_discounted': True
                }
            ),
            args[0]
        )

        self.assertEqual(
            InternalHackleUser(
                identifiers={
                    '$id': 'id',
                    '$userId': 'user_id',
                    '$deviceId': 'device_id',
                    'custom_id': 'custom'
                },
                properties={'age': 42, 'grade': 'GOLD', 'membership': True}),
            args[1]
        )

        self.core.track.assert_called_once()

    def test__track_legacy_event(self):
        event = Hackle.event('purchase', value=4200, age=42, grade='GOLD', membership=True)

        self.sut.track(event, HackleUser.builder().id('user').build())

        tracked_event = self.core.track.call_args[0][0]

        self.assertEqual(
            HackleEvent('purchase', 4200, {'age': 42, 'grade': 'GOLD', 'membership': True}),
            tracked_event
        )

    def test__track_legacy_user(self):
        event = Hackle.event('purchase')
        user = Hackle.user(id='user', age=42, grade='GOLD', membership=True)

        self.sut.track(event, user)

        tracked_user = self.core.track.call_args[0][1]

        self.assertEqual(
            InternalHackleUser(identifiers={'$id': 'user'},
                               properties={'age': 42, 'grade': 'GOLD', 'membership': True}),
            tracked_user
        )

    def test__remote_config(self):
        actual = self.sut.remote_config(HackleUser.builder().id('user').build())
        self.assertIsInstance(actual, HackleRemoteConfigImpl)

    def test__update_user_properties(self):
        operations = PropertyOperations.builder().set('age', 42).build()
        user = HackleUser.builder().id('user').build()

        self.sut.update_user_properties(operations, user)

        args = self.core.track.call_args[0]

        self.assertEqual(
            HackleEvent('$properties', None, {'$set': {'age': 42}}),
            args[0]
        )

    def test__update_user_properties__invalid_operations(self):
        user = HackleUser.builder().id('user').build()

        self.sut.update_user_properties(42, user)

        self.core.assert_not_called()

    def test__update_user_properties__all_operations(self):
        operations = PropertyOperations.builder() \
            .set('name', 'John') \
            .set_once('created_at', '2024-01-01') \
            .unset('old_field') \
            .increment('login_count', 1) \
            .append('tags', 'premium') \
            .append_once('unique_tags', 'vip') \
            .prepend('notifications', 'new_message') \
            .prepend_once('unique_notifications', 'welcome') \
            .remove('blocked_users', 'user123') \
            .clear_all() \
            .build()
        user = HackleUser.builder().id('user').build()

        self.sut.update_user_properties(operations, user)

        args = self.core.track.call_args[0]

        expected_event = HackleEvent('$properties', None, {
            '$set': {'name': 'John'},
            '$setOnce': {'created_at': '2024-01-01'},
            '$unset': {'old_field': '-'},
            '$increment': {'login_count': 1},
            '$append': {'tags': 'premium'},
            '$appendOnce': {'unique_tags': 'vip'},
            '$prepend': {'notifications': 'new_message'},
            '$prependOnce': {'unique_notifications': 'welcome'},
            '$remove': {'blocked_users': 'user123'},
            '$clearAll': {'clearAll': '-'}
        })

        self.assertEqual(expected_event, args[0])
