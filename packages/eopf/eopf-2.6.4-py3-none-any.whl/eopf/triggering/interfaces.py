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
interfaces.py


dataclasses interfaces between parsers and runner

"""


import enum
from dataclasses import dataclass
from typing import Any, List, Optional, Self, Type

from eopf import OpeningMode
from eopf.common.file_utils import AnyPath
from eopf.store import EOProductStore


class PathType(enum.Enum):
    Filename = "filename"
    Folder = "folder"
    Regex = "regex"


@dataclass
class EOBreakPointParserResult:
    ids: list[str]
    all: bool
    store_params: dict[str, Any]
    folder: Optional[AnyPath] = None

    def make_absolute(self, reference: Optional[AnyPath] = None) -> Self:
        if self.folder is not None:
            self.folder = self.folder.make_absolute(reference)
        return self


@dataclass
class EOExternalModuleImportParserResult:
    """
    External module dataclass
    """

    name: str
    nested: bool = False
    alias: Optional[str] = None
    folder: Optional[AnyPath] = None

    def make_absolute(self, reference: Optional[AnyPath] = None) -> Self:
        if self.folder is not None:
            self.folder = self.folder.make_absolute(reference)
        return self


@dataclass
class EOOutputProductParserResult:
    """
    Output product dataclass
    """

    id: str
    store_class: Type[EOProductStore]
    path: AnyPath
    type: PathType
    opening_mode: OpeningMode
    store_type: str
    store_params: dict[str, Any]
    apply_eoqc: bool

    def make_absolute(self, reference: Optional[AnyPath] = None) -> Self:
        self.path = self.path.make_absolute(reference)
        return self


@dataclass
class EOInputProductParserResult:
    """
    Input product dataclass
    """

    id: str
    store_class: Type[EOProductStore]
    path: AnyPath
    type: PathType
    store_type: str
    store_params: dict[str, Any]

    def make_absolute(self, reference: Optional[AnyPath] = None) -> Self:
        self.path = self.path.make_absolute(reference)
        return self


@dataclass
class EOADFStoreParserResult:
    id: str
    path: AnyPath
    store_params: dict[str, Any]

    def make_absolute(self, reference: Optional[AnyPath] = None) -> Self:
        self.path = self.path.make_absolute(reference)
        return self


@dataclass
class EOIOParserResult:
    output_products: list[EOOutputProductParserResult]
    input_products: list[EOInputProductParserResult]
    adfs: list[EOADFStoreParserResult]

    def make_absolute(self, reference: Optional[AnyPath] = None) -> Self:
        for output in self.output_products:
            output.make_absolute(reference)
        for input_ in self.input_products:
            input_.make_absolute(reference)
        for adf in self.adfs:
            adf.make_absolute(reference)
        return self


@dataclass
class EOQCTriggeringConf:
    config_folders: List[AnyPath] | None = None
    parameters: dict[str, Any] | None = None
    update_attrs: bool = True
    report_path: AnyPath | None = None

    def make_absolute(self, reference: Optional[AnyPath] = None) -> Self:
        if self.report_path is not None:
            self.report_path = self.report_path.make_absolute(reference)
        if self.config_folders is not None:
            for f in self.config_folders:
                f.make_absolute(reference)
        return self
