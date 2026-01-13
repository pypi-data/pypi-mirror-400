from hackle.internal.evaluation.evaluator.evaluator import Evaluator
from hackle.internal.model.entities import Experiment
from hackle.internal.user.internal_hackle_user import InternalHackleUser
from hackle.internal.workspace.workspace import Workspace


class ExperimentRequest(Evaluator.Request):
    def __init__(self, workspace, user, experiment, default_variation_key):
        """
        :param Workspace workspace:
        :param InternalHackleUser user:
        :param Experiment experiment:
        :param str default_variation_key:
        """
        super(ExperimentRequest, self).__init__(Evaluator.Key('EXPERIMENT', experiment.id), workspace, user)
        self.__experiment = experiment
        self.__default_variation_key = default_variation_key

    @staticmethod
    def of(workspace, user, experiment, default_variation_key):
        """
        :param Workspace workspace:
        :param InternalHackleUser user:
        :param Experiment experiment:
        :param str default_variation_key:

        :rtype: ExperimentRequest
        """
        return ExperimentRequest(workspace, user, experiment, default_variation_key)

    @staticmethod
    def from_request(requested_by, experiment):
        """
        :param Evaluator.Request requested_by:
        :param Experiment experiment:

        :rtype: ExperimentRequest
        """
        return ExperimentRequest(requested_by.workspace, requested_by.user, experiment, 'A')

    @property
    def experiment(self):
        """
        :rtype: Experiment
        """
        return self.__experiment

    @property
    def default_variation_key(self):
        """
        :rtype: str
        """
        return self.__default_variation_key

    def __str__(self):
        return 'EvaluatorRequest(type={}, key={})'.format(self.__experiment.type, self.__experiment.key)

    def __repr__(self):
        return self.__str__()
