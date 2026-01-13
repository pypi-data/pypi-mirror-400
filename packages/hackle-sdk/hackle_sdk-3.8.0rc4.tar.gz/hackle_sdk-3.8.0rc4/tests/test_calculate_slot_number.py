import csv
import os

from hackle.internal.evaluation.bucket.bucketer import Bucketer
from tests import base


class CalculateSlotNumberTest(base.BaseTest):

    def setUp(self):
        self.bucketer = Bucketer()

    def test_calculate_slot_number(self):
        self.check('resources/bucketing_all.csv')
        self.check('resources/bucketing_alphabetic.csv')
        self.check('resources/bucketing_alphanumeric.csv')
        self.check('resources/bucketing_numeric.csv')
        self.check('resources/bucketing_uuid.csv')

    def check(self, file_name):
        with open(os.path.join(os.path.dirname(__file__), file_name)) as f:
            csv_file = csv.reader(f, delimiter=',', quoting=csv.QUOTE_NONE)
            for row in csv_file:
                seed = int(row[0])
                slot_size = int(row[1])
                user_id = row[2]
                slot_number = int(row[3])

                actual = self.bucketer._calculate_slot_number(user_id, seed, slot_size)
                self.assertEqual(slot_number, actual, row)
