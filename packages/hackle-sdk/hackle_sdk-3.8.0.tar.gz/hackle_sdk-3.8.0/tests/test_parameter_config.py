from tests import base
from hackle.internal.model.entities import ParameterConfiguration


class ParameterConfigurationTest(base.BaseTest):

    def setUp(self):
        self.config = ParameterConfiguration(
            42,
            {
                'string_key': 'string_value',
                'string_empty': '',
                'int_key': 42,
                'zero_int_key': 0,
                'negative_int_key': -1,
                'float_key': 0.42,
                'true_boolean_key': True,
                'false_boolean_key': False
            }
        )

    def test_parameter_config(self):
        self.assertEqual(self.config.get("string_key", "!!"), "string_value")
        self.assertEqual(self.config.get("empty_string_key", "!!"), "!!")
        self.assertEqual(self.config.get("invalid_key", "!!"), "!!")

        self.assertEqual(self.config.get("int_key", 999), 42)
        self.assertEqual(self.config.get("zero_int_key", 999), 0)
        self.assertEqual(self.config.get("negative_int_key", 999), -1)
        self.assertEqual(self.config.get("invalid_int_key", 999), 999)
        self.assertEqual(self.config.get("float_key", 999), 999)

        self.assertEqual(self.config.get("float_key", 0.0), 0.42)
        self.assertEqual(self.config.get("invalid_double_key", 0.0), 0.0)
        self.assertEqual(self.config.get("invalid_double_key", 0.0), 0.0)

    def test_parameter_config_edge_case(self):
        # parameter value exist (not None)
        self.assertEqual(self.config.get("string_key", "!!"), "string_value")

        # parameter value exist (None)
        self.assertEqual(self.config.get("string_key", None), "string_value")

        # parameter value not exist, default (not None)
        self.assertEqual(self.config.get("invalid_string_key", "!!"), "!!")

        # parameter value not exist, default (None)
        self.assertEqual(self.config.get("string_key", None), "string_value")

        # parameter value, default are different type
        self.assertEqual(self.config.get("string_key", 100), 100)
        self.assertEqual(self.config.get("string_key", []), [])

        # parameter key not exist
        self.assertEqual(self.config.get(None, 100), 100)
