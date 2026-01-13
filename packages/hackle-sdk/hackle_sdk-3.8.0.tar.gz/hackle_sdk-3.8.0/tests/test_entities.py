from tests import base
from hackle.internal.model.entities import *


class EntityTest(base.BaseTest):

    def test_base_entity_equals(self):
        self.assertNotEqual('BaseEntity', BaseEntity())

    def test_experiment_get_variation_by_id_or_none(self):
        experiment = Experiment(
            id=1,
            key=1,
            type='AB_TEST',
            identifier_type='$id',
            status='RUNNING',
            version=1,
            execution_version=1,
            variations=[
                Variation(11, 'A', False),
                Variation(22, 'B', False)
            ],
            user_overrides={},
            segment_overrides=[],
            target_audiences=[],
            target_rules=[],
            default_rule=TargetAction('BUCKET', bucket_id=1),
            container_id=None,
            winner_variation_id=None
        )

        self.assertEqual(Variation(11, 'A', False), experiment.get_variation_by_id_or_none(11))
        self.assertIsNone(experiment.get_variation_by_id_or_none(13))

    def test_bucket_get_slot_or_none(self):
        bucket = Bucket(
            1,
            10000,
            [
                Slot(0, 10, 1),
                Slot(10, 20, 2)
            ]
        )

        self.assertEqual(Slot(0, 10, 1), bucket.get_slot_or_none(0))
        self.assertEqual(Slot(0, 10, 1), bucket.get_slot_or_none(9))
        self.assertEqual(Slot(10, 20, 2), bucket.get_slot_or_none(10))
        self.assertEqual(Slot(10, 20, 2), bucket.get_slot_or_none(19))
        self.assertEqual(None, bucket.get_slot_or_none(20))

    def test_completed_experiment(self):
        experiment = Experiment(
            id=1,
            key=1,
            type='AB_TEST',
            identifier_type='$id',
            status='COMPLETED',
            version=1,
            execution_version=1,
            variations=[
                Variation(11, 'A', False),
                Variation(22, 'B', False)
            ],
            user_overrides={
                'a': 11,
                'b': 22
            },
            segment_overrides=[],
            target_audiences=[],
            target_rules=[],
            default_rule=TargetAction('BUCKET', bucket_id=1),
            container_id=None,
            winner_variation_id=22
        )

        self.assertEqual(Variation(22, 'B', False), experiment.winner_variation)
