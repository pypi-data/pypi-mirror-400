from hackle.model import HackleUser
from tests import base


class UserTest(base.BaseTest):

    def test_hackle_user_build(self):
        user = HackleUser.builder() \
            .id("id") \
            .user_id("user_id") \
            .device_id("device_id") \
            .session_id("session_id") \
            .identifier("custom_id_type", "custom_id_value") \
            .identifiers({"custom_1_key": "custom_1_value"}) \
            .property("age", 30) \
            .properties({"grade": "GOLD", "is_payed_user": False}) \
            .build()

        self.assertEqual("id", user.id)
        self.assertEqual("user_id", user.user_id)
        self.assertEqual({
            "$sessionId": "session_id",
            "custom_id_type": "custom_id_value",
            "custom_1_key": "custom_1_value"
        }, user.identifiers)
        self.assertEqual({
            "age": 30,
            "grade": "GOLD",
            "is_payed_user": False
        }, user.properties)
