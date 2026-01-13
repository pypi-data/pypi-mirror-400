from typing import TypedDict

from craft_ai_sdk.sdk import BaseCraftAiSdk


class PipelineTemplateReference(TypedDict):
    name: str
    version: str
    display_name: str
    description: str
    hosting_type: str
    model_family: str


class PipelineTemplate(PipelineTemplateReference):
    enabled: bool


class PipelineTemplateDetails(PipelineTemplate):
    inputs: list[dict]
    outputs: list[dict]
    recommended_inputs_mapping: list[dict]
    recommended_outputs_mapping: list[dict]


def list_pipeline_templates(sdk: BaseCraftAiSdk) -> list[PipelineTemplate]:
    """List all the available pipeline templates.

    Returns:
        :obj:`list` of :obj:`dict`: List of available pipeline templates represented
        as a dict with the following keys:

        * ``"name"`` (:obj:`str`): Name of the pipeline template used as an
            identifier to create the pipeline.
        * ``"version"`` (:obj:`str`): Version of the pipeline template.
        * ``"enabled"`` (:obj:`bool`): Whether the pipeline template can be used to
            create pipelines or not.
        * ``"display_name"`` (:obj:`str`): Display name of the pipeline
            template.
        * ``"description"`` (:obj:`str`): Description of the pipeline template.
        * ``"hosting_type"`` (:obj:`str`): Either ``"self-hosted"`` if the model
            runs on the environment's infrastructure, or ``"private-api"`` if the
            model inference is done through an external API.
        * ``"model_family"`` (:obj:`str`): Model family of the pipeline
            template.
    """

    url = f"{sdk.base_environment_api_url}/pipeline-templates"
    response = sdk._get(url)
    return response["pipeline_templates"]


def get_pipeline_template(sdk: BaseCraftAiSdk, pipeline_template_name: str):
    """Get information about a specific pipeline template. A pipeline template
    could be used to create a pipeline.

    Args:
        pipeline_template_name (str): Name of the pipeline template to retrieve.

    Returns:
        :obj:`dict`: Information on the pipeline template represented as dict
        with the following keys:

        * ``"name"`` (:obj:`str`): Name of the pipeline template used as an
            identifier to create the pipeline.
        * ``"version"`` (:obj:`str`): Version of the pipeline template.
        * ``"enabled"`` (:obj:`bool`): Whether the pipeline template can be used to
            create pipelines or not.
        * ``"display_name"`` (:obj:`str`): Display name of the pipeline
            template.
        * ``"description"`` (:obj:`str`): Description of the pipeline template.
        * ``"hosting_type"`` (:obj:`str`): Either ``"self-hosted"`` if the model
            runs on the environment's infrastructure, or ``"private-api"`` if the
            model inference is done through an external API.
        * ``"model_family"`` (:obj:`str`): Model family of the pipeline
            template.
        * ``"inputs"`` (:obj:`list` of :obj:`dict`): List of inputs of the pipeline
            once created represented as a dict with the following keys:

          * ``"name"`` (:obj:`str`): Input name.
          * ``"data_type"`` (:obj:`str`): Input data type.
          * ``"is_required"`` (:obj:`bool`): Whether the input is required.
          * ``"default_value"`` (:obj:`str`): Input default value.
          * ``"description"`` (:obj:`str`): Output description.

        * ``"outputs"`` (:obj:`list` of :obj:`dict`): List of outputs of the pipeline
          once created represented as a dict with the following keys:

          * ``"name"`` (:obj:`str`): Output name.
          * ``"data_type"`` (:obj:`str`): Output data type.
          * ``"description"`` (:obj:`str`): Output description.

        * ``"recommended_inputs_mapping"`` (:obj:`list` of :obj:`dict`):
          List of recommended inputs mapping for creating a deployment represented
          as a dict with the following keys:

          * ``"pipeline_input_name"`` (:obj:`str`): Name of the input.
          * ``"data_type`` (:obj:`str`): Data type of the input.
          * ``"source`` (:obj:`str`): Source of type of the input. Can be
            "environment_variable", "datastore", "constant", "is_null" "endpoint"
            or "run".
          * ``"endpoint_input_name"`` (:obj:`str`): Name of the input in the
            endpoint execution if source is "endpoint".
          * ``"constant_value"`` (:obj:`str`): Value of the constant if source is
            "constant".
          * ``"environment_variable_name"`` (:obj:`str`): Name of the environment
            variable if source is "environment_variable".
          * ``"is_null"`` (:obj:`bool`): True if source is "is_null".
          * ``"value"``: Value of the input.

        * ``"recommended_outputs_mapping"`` (:obj:`list` of :obj:`dict`):
          List of recommended outputs mapping for creating a deployment represented
          as a dict with the following keys:

          * ``"pipeline_output_name"`` (:obj:`str`): Name of the output.
          * ``"data_type`` (:obj:`str`): Data type of the output.
          * ``"destination`` (:obj:`str`): Destination of type of the output. Can be
            "datastore", "is_null" "endpoint" or "run".
          * ``"endpoint_output_name"`` (:obj:`str`): Name of the output in the
            endpoint execution if destination is "endpoint".
          * ``"is_null"`` (:obj:`bool`): True if destination is "is_null".
          * ``"value"``: Value of the output.
    """

    url = f"{sdk.base_environment_api_url}/pipeline-templates/{pipeline_template_name}"
    return sdk._get(url)
