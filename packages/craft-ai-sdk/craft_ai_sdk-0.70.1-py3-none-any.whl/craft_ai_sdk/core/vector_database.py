from typing import TYPE_CHECKING, TypedDict

from craft_ai_sdk.shared.environments import get_environment_id

from ..sdk import BaseCraftAiSdk
from ..shared.logger import log_action, log_func_result

if TYPE_CHECKING:
    try:
        import weaviate as weaviate_type
    except ModuleNotFoundError:
        pass


class VectorDatabaseCredentials(TypedDict):
    vector_database_url: str
    vector_database_token: str


def get_vector_database_credentials(sdk: BaseCraftAiSdk) -> VectorDatabaseCredentials:
    """Get the credentials of the vector database.

    Returns:
        :obj:`dict`: The vector database credentials, with the following keys:
            * ``"vector_database_url"`` (:obj:`str`): URL of the vector database.
            * ``"vector_database_token"`` (:obj:`str`): Token to connect to the vector
              database.
    """
    environment_id = get_environment_id(sdk)

    vector_database_url = (
        f"{sdk.base_control_api_url}/environments/{environment_id}/vector-database"
    )

    return sdk._get(vector_database_url)


class WeaviateParameters(VectorDatabaseCredentials):
    is_secure: bool
    vector_database_host: str


def _get_weaviate_parameters(sdk: BaseCraftAiSdk):
    credentials = get_vector_database_credentials(sdk)

    is_secure = credentials["vector_database_url"].startswith("https://")

    vector_database_host = (
        credentials["vector_database_url"]
        .replace("http://", "")
        .replace("https://", "")
    ).rstrip("/")

    return WeaviateParameters(
        vector_database_url=credentials["vector_database_url"],
        vector_database_token=credentials["vector_database_token"],
        is_secure=is_secure,
        vector_database_host=vector_database_host,
    )


@log_func_result("Connecting to Weaviate")
def get_weaviate_client(sdk: BaseCraftAiSdk) -> "weaviate_type.WeaviateClient":
    """Initializes and returns a Weaviate client for interacting with the vector
    database.

    Returns:
        :obj:`weaviate.WeaviateClient`: The Weaviate client.
    """
    try:
        import weaviate
    except ModuleNotFoundError:
        raise ModuleNotFoundError(
            "The 'weaviate' package is required to use the vector database. "
            "You can install it with 'pip install weaviate-client'."
        ) from None

    weaviate_parameters = _get_weaviate_parameters(sdk)

    log_action(sdk, "Connecting to Weaviate")

    weaviate_client = weaviate.connect_to_custom(
        http_host=weaviate_parameters["vector_database_host"],
        http_port=8080,
        grpc_host=weaviate_parameters["vector_database_host"],
        grpc_port=8082,
        http_secure=weaviate_parameters["is_secure"],
        grpc_secure=weaviate_parameters["is_secure"],
        headers={
            "craft-vector-database-token": weaviate_parameters["vector_database_token"],
            "craft-vector-database-url": weaviate_parameters["vector_database_url"],
        },
        auth_credentials=None,
    )

    log_action(
        sdk,
        f"Connected to Weaviate, using version {weaviate.__version__}",
    )

    return weaviate_client


@log_func_result("Connecting to Weaviate")
def get_async_weaviate_client(
    sdk: BaseCraftAiSdk,
) -> "weaviate_type.WeaviateAsyncClient":
    """Initializes and returns an async Weaviate client for interacting with the vector
    database.

    Returns:
        :obj:`weaviate.WeaviateAsyncClient`: The Weaviate client.
    """
    try:
        import weaviate
    except ModuleNotFoundError:
        raise ModuleNotFoundError(
            "The 'weaviate' package is required to use the vector database. "
            "You can install it with 'pip install weaviate-client'."
        ) from None

    weaviate_parameters = _get_weaviate_parameters(sdk)

    log_action(sdk, "Connecting to Weaviate")

    weaviate_client = weaviate.use_async_with_custom(
        http_host=weaviate_parameters["vector_database_host"],
        http_port=8080,
        grpc_host=weaviate_parameters["vector_database_host"],
        grpc_port=8082,
        http_secure=weaviate_parameters["is_secure"],
        grpc_secure=weaviate_parameters["is_secure"],
        headers={
            "craft-vector-database-token": weaviate_parameters["vector_database_token"],
            "craft-vector-database-url": weaviate_parameters["vector_database_url"],
        },
        auth_credentials=None,
    )

    log_action(
        sdk,
        f"Connected to Weaviate, using version {weaviate.__version__}",
    )

    return weaviate_client
