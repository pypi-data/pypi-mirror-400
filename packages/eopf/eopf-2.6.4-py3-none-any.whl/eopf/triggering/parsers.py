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
parsers.py

parsers for all


"""
import importlib
import os
from contextlib import nullcontext
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Optional, Type, Union

from dacite import Config, MissingValueError, WrongTypeError, from_dict

from eopf import AnyPath, EOConfiguration, EOZarrStore, OpeningMode
from eopf.common.dtree_utils import datatree_write_accepted_mode
from eopf.dask_utils import DaskContext
from eopf.dask_utils.dask_cluster_type import get_enum_from_value
from eopf.exceptions import TriggeringConfigurationError
from eopf.exceptions.errors import TriggerInvalidWorkflow
from eopf.store import EOProductStore
from eopf.store.store_factory import EOStoreFactory
from eopf.triggering.general_utils import parse_store_params
from eopf.triggering.interfaces import (
    EOADFStoreParserResult,
    EOBreakPointParserResult,
    EOExternalModuleImportParserResult,
    EOInputProductParserResult,
    EOIOParserResult,
    EOOutputProductParserResult,
    EOQCTriggeringConf,
    PathType,
)
from eopf.triggering.workflow import EOProcessorWorkFlow, WorkFlowUnitDescription

# Abstracts


class YamlAdapter:
    KEY: str  # YAML key containing the section
    TARGET_CLASS: type  # final object type after hook

    @classmethod
    def hook(cls, raw: Any) -> Any:
        raise NotImplementedError


def build_dacite_config(section: type[YamlAdapter]) -> Config:
    return Config(strict=False, type_hooks={section.TARGET_CLASS: section.hook, AnyPath: _load_anypath})


def _load_anypath(raw: str) -> AnyPath:
    return AnyPath(os.path.expandvars(raw))


def load_section(data: Dict[str, Any], section: type[Any]) -> Any:
    if issubclass(section, YamlAdapter):
        cfg = build_dacite_config(section)
    else:
        cfg = Config(strict=False, type_hooks={AnyPath: _load_anypath})
    try:
        return from_dict(
            data_class=section,
            data=data,
            config=cfg,
        )
    except (MissingValueError, WrongTypeError) as e:
        raise TriggeringConfigurationError(f"Error on payload {e}") from e


# Breakpoints


@dataclass
class BreakPointRaw:
    ids: list[str]
    all: bool = False
    store_params: dict[str, Any] = field(default_factory=dict)
    folder: Optional[str] = None


@dataclass
class BreakPointSection(YamlAdapter):
    breakpoints: Optional[EOBreakPointParserResult]

    KEY = "breakpoints"
    TARGET_CLASS = EOBreakPointParserResult

    @classmethod
    def hook(cls, raw: dict[str, Any]) -> EOBreakPointParserResult:
        raw_obj: BreakPointRaw = from_dict(BreakPointRaw, raw)
        store_params = parse_store_params(raw_obj.store_params)
        return EOBreakPointParserResult(
            ids=raw_obj.ids,
            all=raw_obj.all,
            folder=AnyPath(raw_obj.folder, **store_params["storage_options"]) if raw_obj.folder is not None else None,
            store_params=store_params,
        )


@dataclass
class ConfigFilesSection:
    config: list[AnyPath] = field(default_factory=list)


@dataclass
class DaskRaw:
    cluster_type: str = "address"
    cluster_config: Optional[dict[str, Any]] = None
    client_config: Optional[dict[str, Any]] = None
    dask_config: Optional[dict[str, Any]] = None
    performance_report_file: Optional[Union[str, Path]] = None


@dataclass
class DaskContextSection(YamlAdapter):
    dask_context: DaskContext | nullcontext[None] = nullcontext()

    KEY = "dask_context"
    TARGET_CLASS = DaskContext

    @classmethod
    def hook(cls, raw: dict[str, Any]) -> DaskContext:
        raw_obj: DaskRaw = from_dict(DaskRaw, raw)

        return DaskContext(
            cluster_type=get_enum_from_value(raw_obj.cluster_type),
            cluster_config=raw_obj.cluster_config,
            client_config=raw_obj.client_config,
            dask_config=raw_obj.dask_config,
            performance_report_file=raw_obj.performance_report_file,
        )


@dataclass
class EnvVarsSection:
    dotenv: list[AnyPath] = field(default_factory=list)


@dataclass
class ExternalModulesSection:

    external_modules: Optional[list[EOExternalModuleImportParserResult]] = field(default_factory=list)


@dataclass
class GeneralConfigurationSection:
    general_configuration: dict[str, Any] = field(default_factory=dict)


# --- utilities functions ---
def get_store_driver_cls(
    path: Optional[str] = None,
    store_type: Optional[str] = None,
    **kwargs: Any,
) -> Type[EOProductStore]:
    """Instantiate an EOProductStore from the given inputs

    Parameters
    ----------
    path: str
        path to the corresponding product
    store_type: str
        key for the EOStoreFactory to retrieve the correct type of store

    Returns
    -------
    Type[EOProductStore]

    See Also
    --------
    eopf.product.store.EOProductStore
    eopf.product.store.store_factory.EOStoreFactory
    """
    if store_type is not None:
        return EOStoreFactory.get_product_store_by_format(store_type)
    if path is not None:
        fspath: AnyPath = AnyPath.cast(path, kwargs=kwargs)
        return EOStoreFactory.get_product_store_by_file(fspath)
    raise TriggeringConfigurationError("Either path or store_type requested")


# --- RAW dataclasses ---


@dataclass
class EOOutputRaw:
    id: str
    path: str
    store_type: str
    store_params: dict[str, Any] = field(default_factory=dict)
    type: str = "filename"
    opening_mode: str = "CREATE"
    apply_eoqc: bool = False


@dataclass
class EOInputRaw:
    id: str
    path: str
    store_type: str
    store_params: dict[str, Any] = field(default_factory=dict)
    type: str = "filename"


@dataclass
class EOADFRaw:
    id: str
    path: str
    store_params: dict[str, Any] = field(default_factory=dict)


# --- Section classes ---
@dataclass
class EOOutputSection(YamlAdapter):
    KEY = "output_products"
    TARGET_CLASS = EOOutputProductParserResult

    @classmethod
    def hook(cls, raw: dict[str, Any]) -> EOOutputProductParserResult:
        raw_obj: EOOutputRaw = from_dict(EOOutputRaw, raw)
        # Check if the store is valid
        if raw_obj.store_type and not EOStoreFactory.check_product_store_available(raw_obj.store_type):
            raise TriggeringConfigurationError(
                f"{raw_obj.store_type} not recognized, should be one of "
                f"{tuple(EOStoreFactory.get_product_stores_available().keys())}.",
            )

        store_params = parse_store_params(raw_obj.store_params)
        store_class = EOStoreFactory.get_product_store_by_format(raw_obj.store_type)
        opening_mode = OpeningMode.cast(raw_obj.opening_mode)

        if store_class == EOZarrStore and EOConfiguration().triggering__use_datatree:
            if opening_mode not in datatree_write_accepted_mode():
                raise TriggeringConfigurationError(f"{opening_mode} not allowed by datatree")

        elif opening_mode not in store_class.allowed_mode():
            raise TriggeringConfigurationError(f"{opening_mode} not allowed by store {store_class.__name__}")

        return EOOutputProductParserResult(
            id=raw_obj.id,
            store_class=store_class,
            path=AnyPath.cast(raw_obj.path, **store_params["storage_options"]),
            type=PathType(raw_obj.type),
            opening_mode=opening_mode,
            store_type=raw_obj.store_type,
            store_params=store_params,
            apply_eoqc=raw_obj.apply_eoqc,
        )


@dataclass
class EOInputSection(YamlAdapter):
    KEY = "input_products"
    TARGET_CLASS = EOInputProductParserResult

    @classmethod
    def hook(cls, raw: dict[str, Any]) -> EOInputProductParserResult:
        raw_obj: EOInputRaw = from_dict(EOInputRaw, raw)

        if raw_obj.store_type and not EOStoreFactory.check_product_store_available(raw_obj.store_type):
            raise TriggeringConfigurationError(
                f"{raw_obj.store_type} not recognized, should be one of "
                f"{tuple(EOStoreFactory.get_product_stores_available().keys())}.",
            )
        store_params = parse_store_params(raw_obj.store_params)
        store_class = EOStoreFactory.get_product_store_by_format(raw_obj.store_type)

        return EOInputProductParserResult(
            id=raw_obj.id,
            store_class=store_class,
            path=AnyPath.cast(raw_obj.path, **store_params["storage_options"]),
            type=PathType(raw_obj.type),
            store_type=raw_obj.store_type,
            store_params=store_params,
        )


@dataclass
class EOADFSection(YamlAdapter):
    KEY = "adfs"
    TARGET_CLASS = EOADFStoreParserResult

    @classmethod
    def hook(cls, raw: dict[str, Any]) -> EOADFStoreParserResult:
        raw_obj: EOADFRaw = from_dict(EOADFRaw, raw)
        store_params = parse_store_params(raw_obj.store_params)
        return EOADFStoreParserResult(
            id=raw_obj.id,
            path=AnyPath.cast(raw_obj.path, **store_params["storage_options"]),
            store_params=store_params,
        )


@dataclass
class EOIOSection(YamlAdapter):

    io: EOIOParserResult

    KEY = "io"
    TARGET_CLASS = EOIOParserResult

    @classmethod
    def hook(cls, raw: dict[str, Any]) -> EOIOParserResult:
        return EOIOParserResult(
            output_products=[EOOutputSection.hook(item) for item in raw["output_products"]],
            input_products=(
                [EOInputSection.hook(item) for item in raw.get("input_products", [])]
                if raw.get("input_products")
                else []
            ),
            adfs=[EOADFSection.hook(item) for item in raw.get("adfs", [])] if raw.get("adfs") else [],
        )


@dataclass
class LoggingFilesSection:
    logging: list[AnyPath] = field(default_factory=list)


@dataclass
class QualityControlSection:

    eoqc: Optional[EOQCTriggeringConf] = None


@dataclass
class SecretSection:
    secret: list[AnyPath] = field(default_factory=list)


@dataclass
class WorkflowRaw:
    name: str
    module: str
    processing_unit: str

    parameters: Dict[str, Any] = field(default_factory=dict)
    inputs: Dict[str, Any] = field(default_factory=dict)
    outputs: Dict[str, Any] = field(default_factory=dict)
    adfs: Dict[str, Any] = field(default_factory=dict)

    step: int = 0
    active: bool = True
    validate: bool = True
    mode: Optional[str] = None


@dataclass
class WorkflowSection(YamlAdapter):
    workflow: EOProcessorWorkFlow

    KEY = "workflow"
    TARGET_CLASS = EOProcessorWorkFlow

    @classmethod
    def hook(cls, raw: list[dict[str, Any]]) -> EOProcessorWorkFlow:
        units = [cls._convert_raw_to_unit(from_dict(WorkflowRaw, subraw)) for subraw in raw]

        return EOProcessorWorkFlow(
            workflow_units=[u for u in units if u is not None],
        )

    @classmethod
    def _convert_raw_to_unit(cls, raw_obj: WorkflowRaw) -> Optional[WorkFlowUnitDescription]:
        # inactive → trivial object
        if not raw_obj.active:
            return None

        # dynamic import
        try:
            module = importlib.import_module(raw_obj.module)
            try:
                unit_class = getattr(module, raw_obj.processing_unit)
                unit = unit_class(raw_obj.name)
            except AttributeError as e:
                raise TriggeringConfigurationError(
                    f"Class {raw_obj.processing_unit} not found in module {raw_obj.module} for workflow",
                ) from e
        except (
            ImportError,
            ModuleNotFoundError,
            SyntaxError,
            AttributeError,
            PermissionError,
            ValueError,
            TypeError,
            OSError,
            NameError,
        ) as e:
            raise TriggeringConfigurationError(f"Error while importing module {raw_obj.module} : {type(e)} {e}") from e

        mode = raw_obj.mode or unit.get_default_mode()

        # validations
        req_inputs = unit.get_mandatory_input_list(**raw_obj.parameters)
        if not all(k in raw_obj.inputs for k in req_inputs):
            raise TriggerInvalidWorkflow(
                f"Missing input for unit {raw_obj.module}.{raw_obj.processing_unit}:{raw_obj.name},"
                f" provided {raw_obj.inputs.keys()} "
                f"while requested {unit.get_mandatory_input_list(**raw_obj.parameters)}",
            )

        req_adfs = unit.get_mandatory_adf_list(**raw_obj.parameters)
        if not all(k in raw_obj.adfs for k in req_adfs):
            raise TriggerInvalidWorkflow(
                f"Missing input adf for unit {raw_obj.module}.{raw_obj.processing_unit}:{raw_obj.name}, "
                f"provided {raw_obj.adfs.keys()} "
                f"while requested {unit.get_mandatory_adf_list(**raw_obj.parameters)}",
            )

        return WorkFlowUnitDescription(
            raw_obj.active,
            mode,
            unit,
            raw_obj.inputs,
            raw_obj.adfs,
            raw_obj.outputs,
            raw_obj.parameters,
            raw_obj.step,
            raw_obj.validate,
        )
