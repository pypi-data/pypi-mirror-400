from hackle.internal.evaluation.evaluator.evaluator import Evaluator, ContextualEvaluator


class DelegatingEvaluator(Evaluator):

    def __init__(self):
        super(DelegatingEvaluator, self).__init__()
        self.__evaluators = []

    def add(self, evaluator):
        """
        :param ContextualEvaluator evaluator:
        """
        self.__evaluators.append(evaluator)

    def evaluate(self, request, context):
        for evaluator in self.__evaluators:
            if evaluator.supports(request):
                return evaluator.evaluate(request, context)
        raise Exception('Unsupported Evaluator.Request [{}]'.format(request))
