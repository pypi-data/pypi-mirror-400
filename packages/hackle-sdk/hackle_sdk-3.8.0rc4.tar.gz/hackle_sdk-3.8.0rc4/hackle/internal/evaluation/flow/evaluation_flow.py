from hackle.decision import DecisionReason
from hackle.internal.evaluation.evaluator.evaluator import Evaluator
from hackle.internal.evaluation.evaluator.experiment.experiment_evaluation import ExperimentEvaluation
from hackle.internal.evaluation.evaluator.experiment.experiment_request import ExperimentRequest


class EvaluationFlow(object):

    def __init__(self, flow_evaluator=None, next_flow=None):
        """
        :param hackle.internal.evaluation.flow.flow_evaluator.FlowEvaluator or None flow_evaluator:
        :param EvaluationFlow or None next_flow:
        """
        self.__flow_evaluator = flow_evaluator
        self.__next_flow = next_flow

    @staticmethod
    def of(*flow_evaluators):
        flow = EvaluationFlow()
        for flow_evaluator in reversed(flow_evaluators):
            flow = EvaluationFlow(flow_evaluator, flow)
        return flow

    @property
    def flow_evaluator(self):
        """
        :rtype: hackle.internal.evaluation.flow.flow_evaluator.FlowEvaluator or None
        """
        return self.__flow_evaluator

    @property
    def next_flow(self):
        """
        :rtype: EvaluationFlow or None
        """
        return self.__next_flow

    @property
    def is_end(self):
        """
        :rtype: bool
        """
        return self.__flow_evaluator is None or self.__next_flow is None

    def evaluate(self, request, context):
        """
        :param ExperimentRequest request:
        :param Evaluator.Context context:

        :rtype: ExperimentEvaluation
        """
        if self.is_end:
            return ExperimentEvaluation.of_default(request, context, DecisionReason.TRAFFIC_NOT_ALLOCATED)
        else:
            return self.__flow_evaluator.evaluate(request, context, self.__next_flow)
