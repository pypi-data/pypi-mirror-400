from typing import Optional, Union
import requests
import urllib3
import io

from ... import api
from .. import _dtos

__all__ = ["get_resource_file", "update_instance_resource"]


def get_resource_file(
    resource_file_id: str,
    model_instance_id: Optional[str] = None,
    api_credentials: Optional[api.OIAnalyticsAPICredentials] = None,
):
    # Get credentials from environment if not provided
    if api_credentials is None:
        api_credentials = api.get_default_oianalytics_credentials()

    # Get model execution from environment if not provided
    if model_instance_id is None:
        model_instance_id = _dtos.get_default_model_execution().pythonModelInstance.id

    if model_instance_id == _dtos.get_default_model_execution().pythonModelInstance.id:
        resource_files = _dtos.get_default_model_execution().find_inputs_by_types(
            "FILE"
        )
        for rf in resource_files:
            if rf.value == resource_file_id:
                resource_file_url = rf.url
                if resource_file_url is not None:
                    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
                    return io.BytesIO(
                        requests.get(resource_file_url, verify=False).content
                    )

    # Query endpoint
    url = f"{api_credentials.base_url}/api/oianalytics/python-model-instances/{model_instance_id}/resources/{resource_file_id}/content"
    response = requests.get(
        url=url,
        **api_credentials.auth_kwargs,
    )

    # Output
    response.raise_for_status()
    return io.BytesIO(response.content)


def update_instance_resource(
    file_content: Union[io.StringIO, io.BytesIO],
    file_name: str,
    resource_file_id: str,
    model_instance_id: Optional[str] = None,
    api_credentials: Optional[api.OIAnalyticsAPICredentials] = None,
):
    # Get credentials from environment if not provided
    if api_credentials is None:
        api_credentials = api.get_default_oianalytics_credentials()

    # Get model execution from environment if not provided
    if model_instance_id is None:
        model_instance_id = _dtos.get_default_model_execution().pythonModelInstance.id

    # Query endpoint
    url = f"{api_credentials.base_url}/api/oianalytics/python-model-instances/{model_instance_id}/resources/{resource_file_id}/content"
    response = requests.post(
        url=url,
        files={"file": (file_name, file_content)},
        **api_credentials.auth_kwargs,
    )

    # Output
    response.raise_for_status()
    return response.status_code
