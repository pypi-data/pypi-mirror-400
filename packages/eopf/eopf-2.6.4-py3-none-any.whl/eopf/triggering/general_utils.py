#
# Copyright (C) 2025 ESA
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""
general_utils.py

Utilities for triggering parsing

"""
from typing import Any, Optional

from eopf.common.functions_utils import expand_env_var_in_dict
from eopf.config.config import EOConfiguration
from eopf.exceptions import (
    MissingConfigurationParameterError,
)


def parse_store_params(store_params: dict[str, Any]) -> dict[str, Any]:
    """Retrieve store parameters depending on the used secrets_type"""
    s3_alias = store_params.pop("s3_secret_alias", None)
    storage_options: Optional[dict[str, Any]] = store_params.pop("storage_options", None)
    if s3_alias is not None:
        s3_cloud = EOConfiguration().secrets(s3_alias)
        if (
            ("key" not in s3_cloud)
            or ("secret" not in s3_cloud)
            or ("endpoint_url" not in s3_cloud)
            or ("region_name" not in s3_cloud)
        ):
            raise MissingConfigurationParameterError

        store_params["storage_options"] = {
            "key": s3_cloud["key"],
            "secret": s3_cloud["secret"],
            "client_kwargs": {"endpoint_url": s3_cloud["endpoint_url"], "region_name": s3_cloud["region_name"]},
        }
    elif storage_options is not None:
        store_params["storage_options"] = expand_env_var_in_dict(storage_options)
    else:
        # nothing provided
        store_params["storage_options"] = {}

    return store_params
