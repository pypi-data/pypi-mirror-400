import abc

from six import add_metaclass

from hackle.internal.model.entities import Experiment
from hackle.internal.user.internal_hackle_user import InternalHackleUser
from hackle.internal.workspace.workspace import Workspace


@add_metaclass(abc.ABCMeta)
class Evaluator(object):

    @abc.abstractmethod
    def evaluate(self, request, context):
        """
        :param Evaluator.Request request:
        :param Evaluator.Context context:

        :rtype: Evaluator.Evaluation
        """
        pass

    class Key(object):
        def __init__(self, type_, id_):
            """
            :param str type_:
            :param int id_:
            """
            self.__type = type_
            self.__id = id_

        @property
        def type(self):
            """
            :rtype: str
            """
            return self.__type

        @property
        def id(self):
            """
            :rtype: int
            """
            return self.__id

        def __eq__(self, other):
            if not isinstance(other, Evaluator.Key):
                return False
            return self.__type == other.__type and self.__id == other.__id

        def __ne__(self, other):
            return not self.__eq__(other)

        def __str__(self):
            return "Evaluator.Key(type={}, id={})".format(self.__type, self.__id)

        def __repr__(self):
            return self.__str__()

    @add_metaclass(abc.ABCMeta)
    class Request(object):

        def __init__(self, key, workspace, user):
            """
            :param Evaluator.Key key:
            :param Workspace workspace:
            :param InternalHackleUser user:
            """
            self.__key = key
            self.__workspace = workspace
            self.__user = user

        @property
        def key(self):
            """
            :rtype: Evaluator.Key
            """
            return self.__key

        @property
        def workspace(self):
            """
            :rtype: Workspace
            """
            return self.__workspace

        @property
        def user(self):
            """
            :rtype: InternalHackleUser
            """
            return self.__user

        def __eq__(self, other):
            if not isinstance(other, Evaluator.Request):
                return False
            return self.__key == other.__key

        def __ne__(self, other):
            return not self.__eq__(other)

        def __str__(self):
            return 'Evaluator.Request({}, {})'.format(self.__key.type, self.__key.id)

        def __repr__(self):
            return self.__str__()

    @add_metaclass(abc.ABCMeta)
    class Evaluation(object):
        def __init__(self, reason, target_evaluations):
            """
            :param str reason:
            :param list[Evaluator.Evaluation] target_evaluations:
            """
            self.__reason = reason
            self.__target_evaluations = target_evaluations

        @property
        def reason(self):
            """
            :rtype: str
            """
            return self.__reason

        @property
        def target_evaluations(self):
            """
            :rtype: list[Evaluator.Evaluation]
            """
            return self.__target_evaluations

    class Context(object):
        def __init__(self):
            self.__stack = []
            self.__evaluations = []

        @property
        def stack(self):
            """
            :rtype: list[Evaluator.Request]
            """
            return list(self.__stack)

        @property
        def target_evaluations(self):
            """
            :rtype: list[Evaluator.Evaluation]
            """
            return list(self.__evaluations)

        def contains_request(self, request):
            """
            :param Evaluator.Request request:

            :rtype: bool
            """
            return request in self.__stack

        def add_request(self, request):
            """
            :param Evaluator.Request request:
            """
            self.__stack.append(request)

        @abc.abstractmethod
        def remove_request(self, request):
            """
            :param Evaluator.Request request:
            """
            self.__stack.remove(request)

        @abc.abstractmethod
        def get_evaluation_or_none(self, experiment):
            """
            :param Experiment experiment:
            :rtype: Evaluator.Evaluation or None
            """
            for evaluation in self.__evaluations:
                from hackle.internal.evaluation.evaluator.experiment.experiment_evaluation import ExperimentEvaluation
                if isinstance(evaluation, ExperimentEvaluation) and evaluation.experiment.id == experiment.id:
                    return evaluation
            return None

        @abc.abstractmethod
        def add_evaluation(self, evaluation):
            """
            :param Evaluator.Evaluation evaluation:
            """
            self.__evaluations.append(evaluation)

    @staticmethod
    def context():
        """
        :rtype: Evaluator.Context
        """
        return Evaluator.Context()


@add_metaclass(abc.ABCMeta)
class ContextualEvaluator(Evaluator):

    @abc.abstractmethod
    def supports(self, request):
        """
        :param Evaluator.Request request:

        :rtype: bool
        """
        pass

    @abc.abstractmethod
    def evaluate_internal(self, request, context):
        """
        :param Evaluator.Request request:
        :param Evaluator.Context context:

        :rtype: Evaluator.Evaluation
        """
        pass

    def evaluate(self, request, context):
        if context.contains_request(request):
            stack = context.stack + [request]
            raise Exception('Circular evaluation has occurred [{}]'.format(' - '.join(map(str, stack))))
        context.add_request(request)
        try:
            return self.evaluate_internal(request, context)
        finally:
            context.remove_request(request)
