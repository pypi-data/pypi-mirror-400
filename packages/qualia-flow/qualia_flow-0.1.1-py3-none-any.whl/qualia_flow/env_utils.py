import os
from urllib.parse import urlparse


def get_mlflow_env():

    tracking_uri = os.getenv("MLFLOW_TRACKING_URI", None)

    while tracking_uri is None or (not validate_mlflow_tracking_uri(tracking_uri)):
        tracking_uri = input(
            "Enter MLflow tracking URI (or press Enter for default): "
        ).strip()
        print(f"Using default: {tracking_uri}")
    return tracking_uri


def validate_mlflow_tracking_uri(tracking_uri: str) -> bool:
    """
    Validating mlflow URI
    :param tracking_uri: Description
    :type tracking_uri: str
    :return: Description
    :rtype: bool
    """
    if len(tracking_uri) == 0:
        print("Empty MLflow tracking URI")
        return False

    try:
        parsed_url = urlparse(tracking_uri)
        if parsed_url.scheme not in ("https", "sqlite"):
            print(f"Unsupported tracking uri scheme: {parsed_url.scheme}")
            return False
        return True

    except (TypeError, ValueError) as e:
        print(f"Invalid tracking url : {tracking_uri}, {str(e)}")
        return False
