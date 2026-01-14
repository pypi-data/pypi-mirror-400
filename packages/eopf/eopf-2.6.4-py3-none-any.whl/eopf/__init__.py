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
"""Earth Observation Platform Core Python Modules"""

__version__ = "2.6.4"

from eopf.common import OpeningMode
from eopf.common.file_utils import AnyPath
from eopf.config import EOConfiguration
from eopf.logging import EOLogging
from eopf.product.eo_container import EOContainer
from eopf.product.eo_group import EOGroup
from eopf.product.eo_product import EOProduct
from eopf.product.eo_variable import EOVariable
from eopf.store.convert import convert
from eopf.store.safe import EOSafeStore
from eopf.store.zarr import EOZarrStore

# More features to be imported and listed here
__all__ = [
    "__version__",
    "EOProduct",
    "EOVariable",
    "EOGroup",
    "EOContainer",
    "EOSafeStore",
    "EOZarrStore",
    "convert",
    "EOConfiguration",
    "EOLogging",
    "OpeningMode",
    "AnyPath",
]
