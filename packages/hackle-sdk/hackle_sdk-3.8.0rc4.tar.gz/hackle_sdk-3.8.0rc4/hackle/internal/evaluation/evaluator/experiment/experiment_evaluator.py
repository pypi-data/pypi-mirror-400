from hackle.internal.evaluation.evaluator.evaluator import ContextualEvaluator, Evaluator
from hackle.internal.evaluation.evaluator.experiment.experiment_evaluation import ExperimentEvaluation
from hackle.internal.evaluation.evaluator.experiment.experiment_request import ExperimentRequest
from hackle.internal.evaluation.flow.evaluation_flow_factory import EvaluationFlowFactory


class ExperimentEvaluator(ContextualEvaluator):

    def __init__(self, evaluation_flow_factory):
        """
        :param EvaluationFlowFactory evaluation_flow_factory:
        """
        super(ExperimentEvaluator, self).__init__()
        self.__evaluation_flow_factory = evaluation_flow_factory

    def supports(self, request):
        return isinstance(request, ExperimentRequest)

    def evaluate_internal(self, request, context):
        """
        :param ExperimentRequest request:
        :param Evaluator.Context context:

        :rtype: ExperimentEvaluation
        """
        evaluation_flow = self.__evaluation_flow_factory.get_evaluation_flow(request.experiment.type)
        return evaluation_flow.evaluate(request, context)
