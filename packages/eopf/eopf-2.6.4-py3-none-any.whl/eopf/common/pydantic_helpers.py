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
pydantic_helpers.py

Pydantic helpers common

"""

from typing import Annotated, Any, Optional, Self

from pydantic import BaseModel, Field, model_validator


# --- Shared base class for regex specs ---
class BaseRegexSpec(BaseModel):
    """
    Base regex model to allow min/max occurs
    """

    min_occurs: Annotated[int, Field(ge=0, description="Minimum number of matches required")] = 1
    max_occurs: Annotated[
        Optional[int],
        Field(ge=1, description="Maximum number of matches allowed (None = unlimited)"),
    ] = None

    @model_validator(mode="before")
    def normalize_unbounded(cls, values: dict[str, Any]) -> dict[str, Any]:
        """
        Normalize min/max
        Parameters
        ----------
        values

        Returns
        -------

        """
        max_occurs = values.get("max_occurs")
        if isinstance(max_occurs, str) and max_occurs.lower() in {
            "inf",
            "infinite",
            "unbounded",
        }:
            values["max_occurs"] = None
        return values

    @model_validator(mode="after")
    def validate_cardinality(self) -> Self:
        if self.max_occurs is not None and self.max_occurs < self.min_occurs:
            raise ValueError("max_occurs must be >= min_occurs (or None)")
        return self
