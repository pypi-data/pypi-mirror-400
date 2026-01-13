from hackle.internal.metrics.metrics import Metrics


class DecisionMetrics:

    @staticmethod
    def experiment(sample, key, decision):
        """
        :param hackle.internal.metrics.timer.TimerSample sample:
        :param int key:
        :param decision.ExperimentDecision decision:
        """
        tags = {
            "key": str(key),
            "variation": decision.variation,
            "reason": decision.reason
        }
        timer = Metrics.timer("experiment.decision", tags)
        sample.stop(timer)

    @staticmethod
    def feature_flag(sample, key, decision):
        """
        :param hackle.internal.metrics.timer.TimerSample sample:
        :param int key:
        :param decision.FeatureFlagDecision decision:
        """
        tags = {
            "key": str(key),
            "on": "true" if decision.is_on else "false",
            "reason": decision.reason
        }
        timer = Metrics.timer("feature.flag.decision", tags)
        sample.stop(timer)

    @staticmethod
    def remote_config(sample, key, decision):
        """
        :param hackle.internal.metrics.timer.TimerSample sample:
        :param str key:
        :param decision.RemoteConfigDecision decision:
        """
        tags = {
            "key": key,
            "reason": decision.reason
        }
        timer = Metrics.timer("remote.config.decision", tags)
        sample.stop(timer)
