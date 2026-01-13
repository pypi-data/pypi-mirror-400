from unittest import TestCase

from hackle.model import PropertyOperations


class PropertyOperationsTest(TestCase):

    def test_operations(self):
        operations = PropertyOperations.builder() \
            .set("set1", 42) \
            .set("set2", ["a", "b"]) \
            .set("set2", "set2") \
            .set_once("setOnce", 43) \
            .unset("unset") \
            .increment("increment", 44) \
            .append("append", 45) \
            .append_once("appendOnce", 46) \
            .prepend("prepend", 47) \
            .prepend_once("prependOnce", 48) \
            .remove("remove", 49) \
            .clear_all() \
            .build()

        self.assertEqual(
            {
                '$set': {'set1': 42, 'set2': ['a', 'b']},
                '$setOnce': {'setOnce': 43},
                '$unset': {'unset': '-'},
                '$increment': {'increment': 44},
                '$append': {'append': 45},
                '$appendOnce': {'appendOnce': 46},
                '$prepend': {'prepend': 47},
                '$prependOnce': {'prependOnce': 48},
                '$remove': {'remove': 49},
                '$clearAll': {'clearAll': '-'},
            },
            dict(operations)
        )

        event = operations.to_event()

        self.assertEqual('$properties', event.key)
        self.assertEqual(
            {
                '$set': {'set1': 42, 'set2': ['a', 'b']},
                '$setOnce': {'setOnce': 43},
                '$unset': {'unset': '-'},
                '$increment': {'increment': 44},
                '$append': {'append': 45},
                '$appendOnce': {'appendOnce': 46},
                '$prepend': {'prepend': 47},
                '$prependOnce': {'prependOnce': 48},
                '$remove': {'remove': 49},
                '$clearAll': {'clearAll': '-'},
            },
            event.properties
        )
