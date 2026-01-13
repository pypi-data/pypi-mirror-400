from hackle.internal.evaluation.evaluator.evaluator import Evaluator
from hackle.internal.evaluation.evaluator.experiment.experiment_request import ExperimentRequest
from hackle.internal.model.entities import Experiment, ParameterConfiguration, Variation


class ExperimentEvaluation(Evaluator.Evaluation):
    def __init__(self, reason, target_evaluations, experiment, variation_id, variation_key, config):
        """
        :param str reason:
        :param list[Evaluator.Evaluation] target_evaluations:
        :param Experiment experiment:
        :param int or None variation_id:
        :param str variation_key:
        :param ParameterConfiguration or None config:
        """
        super(ExperimentEvaluation, self).__init__(reason, target_evaluations)
        self.__experiment = experiment
        self.__variation_id = variation_id
        self.__variation_key = variation_key
        self.__config = config

    @staticmethod
    def of(request, context, variation, reason):
        """
        :param ExperimentRequest request:
        :param Evaluator.Context context:
        :param Variation variation:
        :param str reason:

        :rtype: ExperimentEvaluation
        """
        parameter_configuration = None
        parameter_configuration_id = variation.parameter_configuration_id
        if parameter_configuration_id is not None:
            parameter_configuration = request.workspace.get_parameter_configuration_or_none(parameter_configuration_id)
            if parameter_configuration is None:
                raise Exception('ParameterConfiguration[{}]'.format(parameter_configuration_id))

        return ExperimentEvaluation(
            reason,
            context.target_evaluations,
            request.experiment,
            variation.id,
            variation.key,
            parameter_configuration
        )

    @staticmethod
    def of_default(request, context, reason):
        """
        :param ExperimentRequest request:
        :param Evaluator.Context context:
        :param str reason:

        :rtype: ExperimentEvaluation
        """
        variation = request.experiment.get_variation_by_key_or_none(request.default_variation_key)
        if variation is not None:
            return ExperimentEvaluation.of(request, context, variation, reason)
        else:
            return ExperimentEvaluation(
                reason,
                context.target_evaluations,
                request.experiment,
                None,
                request.default_variation_key,
                None
            )

    @property
    def experiment(self):
        """
        :rtype: Experiment
        """
        return self.__experiment

    @property
    def variation_id(self):
        """
        :rtype: int or None
        """
        return self.__variation_id

    @property
    def variation_key(self):
        """
        :rtype: str
        """
        return self.__variation_key

    @property
    def config(self):
        """
        :rtype: ParameterConfiguration or None
        """
        return self.__config

    def copy_with(self, reason):
        """
        :param str reason:
        :rtype: ExperimentEvaluation
        """
        return ExperimentEvaluation(
            reason,
            self.target_evaluations,
            self.experiment,
            self.variation_id,
            self.variation_key,
            self.config
        )
