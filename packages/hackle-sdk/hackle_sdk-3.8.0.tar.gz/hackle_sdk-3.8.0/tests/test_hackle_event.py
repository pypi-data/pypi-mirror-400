from hackle.model import HackleEvent, Event
from tests import base


class HackleEventTest(base.BaseTest):

    def test_build(self):
        event = HackleEvent.builder("purchase") \
            .value(42.0) \
            .property("k1", "v1") \
            .property("k2", 2) \
            .property("arr", [42, 43]) \
            .properties({"k3": True}) \
            .build()

        self.assertTrue(event.is_valid)
        self.assertEqual("purchase", event.key)
        self.assertEqual(42.0, event.value)
        self.assertEqual(4, len(event.properties))
        self.assertEqual({"k1": "v1", "k2": 2, "arr": [42, 43], "k3": True}, event.properties)

    def test_from_event(self):
        event = Event("purchase", 42.42, {"k": "v"})
        hackle_event = HackleEvent.from_event(event)
        self.assertEqual(HackleEvent.builder("purchase").value(42.42).property("k", "v").build(), hackle_event)
        self.assertEqual(hackle_event, HackleEvent.from_event(hackle_event))

    def test_invalid_event(self):
        self.assertFalse(HackleEvent.builder(None).build().is_valid)
        self.assertFalse(HackleEvent.builder("k").value("42").build().is_valid)
        self.assertFalse(HackleEvent("key", 42, "42").is_valid)
