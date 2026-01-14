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
validation.py

Processing Unit input/output validation

"""

import re
from typing import (
    TYPE_CHECKING,
    Annotated,
    Any,
    Dict,
    Iterable,
    List,
    Literal,
    Mapping,
    Optional,
    Self,
    Tuple,
    Union,
    cast,
)

from pydantic import BaseModel, Field, model_validator
from xarray import DataTree

from eopf import EOContainer, EOLogging, EOProduct
from eopf.common.pydantic_helpers import BaseRegexSpec
from eopf.product.eo_container_validation import (
    EOContainerModel,
    container_to_model,
    validate_container_against_model,
)
from eopf.product.eo_product_validation import (
    EOProductModel,
    product_to_model,
    validate_product_against_model,
)
from eopf.product.eo_validation import AnomalyDescriptor

DataTypeSpec = Annotated[
    Union[EOProductModel, EOContainerModel],
    Field(discriminator="type"),
]

if TYPE_CHECKING:
    from eopf.computing.abstract import DataType, MappingAuxiliary, MappingDataType


class DataTypeModel(BaseRegexSpec):
    type: Literal["product", "container"]
    spec: Union[EOProductModel, EOContainerModel]
    iterable_allowed: bool = False

    @model_validator(mode="before")
    def discriminate_spec(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        """Pick the right model for 'spec' depending on 'type'."""
        data_type = values.get("type")
        spec = values.get("spec", {})

        if data_type == "product":
            values["spec"] = EOProductModel.model_validate(spec)
        elif data_type == "container":
            values["spec"] = EOContainerModel.model_validate(spec)
        else:
            raise ValueError(f"Unknown type: {data_type}")

        return values


class AdfSpec(BaseModel):
    required: Annotated[bool, Field(description="Whether this ADF is mandatory")] = True


# --- Specialized regex specs ---


class ParameterSpec(BaseModel):
    """Defines an optional runtime parameter (a **kwarg)."""

    required: Annotated[bool, Field(description="Whether this ADF is mandatory")] = True


class AdfRegexSpec(BaseRegexSpec):
    spec: AdfSpec = Field(..., description="ADF specification")


# --- Mode configuration ---
class ModeConfig(BaseModel):
    inputs: Dict[str, DataTypeModel] = Field(
        default_factory=dict,
        description="Inputs required for this mode (keys may be regex)",
    )
    adfs: Dict[str, AdfRegexSpec] = Field(
        default_factory=dict,
        description="ADFs required for this mode (keys may be regex)",
    )
    outputs: Dict[str, DataTypeModel] = Field(
        default_factory=dict,
        description="Outputs generated in this mode (keys may be regex)",
    )
    parameters: Dict[str, ParameterSpec] = Field(default_factory=dict)

    @model_validator(mode="after")
    def validate_regex_keys(self) -> Self:
        """Ensure all dict keys are valid regex patterns."""
        for group_name, mapping in [
            ("inputs", self.inputs),
            ("adfs", self.adfs),
            ("outputs", self.outputs),
        ]:
            for key in cast(dict[str, Any], mapping).keys():
                try:
                    re.compile(key)
                except re.error:
                    raise ValueError(f"Invalid regex in {group_name}: {key}")
        return self


# --- Processor metadata ---
class EOProcessingModel(BaseModel):
    available_modes: list[str] = Field(..., description="All supported processing modes")
    default_mode: str = Field(..., description="Default processing mode")
    modes_config: Dict[str, ModeConfig] = Field(..., description="Per-mode configuration")

    @model_validator(mode="after")
    def validate_modes(self) -> Self:
        if self.default_mode not in self.available_modes:
            raise ValueError("default_mode must be one of available_modes")
        if self.default_mode not in self.modes_config:
            raise ValueError("modes must include a config for default_mode")
        missing_modes = set(self.available_modes) - set(self.modes_config.keys())
        if missing_modes:
            raise ValueError(f"modes is missing configs for: {', '.join(missing_modes)}")
        return self


##################################################
# ACtual validation part
##################################################
def validate_run_parameters(
    processing_model: "EOProcessingModel",
    inputs: "MappingDataType",
    mode: Optional[str] = None,
    adfs: Optional["MappingAuxiliary"] = None,
    validate_model: bool = False,
    **kwargs: Any,
) -> None:
    """
    Validates that user-provided inputs/adfs match the processor's declared ModeConfig.
    Raises ValueError or TypeError on mismatch.
    """
    mode = regularize_mode(processing_model, mode)
    adfs = adfs or {}

    if mode not in processing_model.modes_config:
        raise ValueError(f"Unknown mode '{mode}'. Must be one of: {list(processing_model.modes_config.keys())}")

    mode_config = processing_model.modes_config[mode]
    # --- validate inputs ---
    _validate_inputs(mode_config.inputs, inputs, validate_model)

    # --- validate ADFs ---
    _validate_adfs(mode_config.adfs, adfs)

    # --- validate kwargs ---
    _validate_kwargs(mode_config.parameters, **kwargs)


def validate_output_models(
    processing_model: "EOProcessingModel",
    outputs: "MappingDataType",
    mode: Optional[str] = None,
    validate_model: bool = False,
) -> None:
    """
    Validates the outputs provided.
    Raises ValueError or TypeError on mismatch.
    """
    mode = regularize_mode(processing_model, mode)
    if mode not in processing_model.modes_config:
        raise ValueError(f"Unknown mode '{mode}'. Must be one of: {list(processing_model.modes_config.keys())}")

    mode_config = processing_model.modes_config[mode]
    # --- validate inputs ---
    _validate_outputs(mode_config.outputs, outputs, validate_model)


def validate_input_models(
    processing_model: "EOProcessingModel",
    inputs: "MappingDataType",
    mode: Optional[str] = None,
    validate_model: bool = False,
) -> None:
    """

    Validate input model

    Parameters
    ----------
    processing_model
    inputs
    mode
    validate_model

    Returns
    -------

    """
    mode = regularize_mode(processing_model, mode)
    if mode not in processing_model.modes_config:
        raise ValueError(f"Unknown mode '{mode}'. Must be one of: {list(processing_model.modes_config.keys())}")

    mode_config = processing_model.modes_config[mode]
    # --- validate inputs ---
    _validate_inputs(mode_config.inputs, inputs, validate_model)


def validate_input_keys(
    processing_model: Optional["EOProcessingModel"],
    input_keys: List[str],
    mode: Optional[str] = None,
) -> None:
    """
    Validates the list of input provided has all the mandatories.
    Raises ValueError or TypeError on mismatch.
    Parameters
    ----------
    processing_model
    input_keys
    mode

    Returns
    -------

    """
    if processing_model is None:
        return
    mode = regularize_mode(processing_model, mode)

    input_model = processing_model.modes_config[mode].inputs
    # --- validate input keys ---
    for user_key in input_keys:
        matched = match_regex_key(user_key, input_model)
        if not matched:
            raise ValueError(f"Unexpected input name '{user_key}' — no declared regex matches it.")

    # --- Check for missing declared inputs ---
    for pattern, spec in input_model.items():
        # Find all user inputs that match this declared pattern
        matches = [k for k in input_keys if re.fullmatch(pattern, k)]
        count = len(matches)

        if count < spec.min_occurs:
            raise ValueError(
                f"Missing inputs matching pattern '{pattern}' — " f"found {count}, requires at least {spec.min_occurs}",
            )

        if spec.max_occurs is not None and count > spec.max_occurs:
            raise ValueError(
                f"Too many inputs matching pattern '{pattern}' — " f"found {count}, max allowed is {spec.max_occurs}",
            )


def validate_adf_models(
    processing_model: "EOProcessingModel",
    adfs: "MappingAuxiliary",
    mode: Optional[str] = None,
) -> None:
    """
    Validate adf
    Parameters
    ----------
    processing_model
    adfs
    mode

    Returns
    -------

    """
    mode = regularize_mode(processing_model, mode)
    if mode not in processing_model.modes_config:
        raise ValueError(f"Unknown mode '{mode}'. Must be one of: {list(processing_model.modes_config.keys())}")

    mode_config = processing_model.modes_config[mode]
    # --- validate inputs ---
    _validate_adfs(mode_config.adfs, adfs)


def validate_adf_keys(
    processing_model: Optional["EOProcessingModel"],
    adf_keys: List[str],
    mode: Optional[str] = None,
) -> None:
    """
    Validates the list of adfs provided has all the mandatories.
    Raises ValueError or TypeError on mismatch.
    Parameters
    ----------
    processing_model
    adf_keys
    mode

    Returns
    -------

    """
    if processing_model is None:
        return

    mode = regularize_mode(processing_model, mode)

    adfs_model = processing_model.modes_config[mode].adfs
    # --- validate input keys ---
    for user_key in adf_keys:
        matched = match_regex_key(user_key, adfs_model)
        if not matched:
            raise ValueError(f"Unexpected adf name '{user_key}' — no declared regex matches it.")

    # --- Check for missing declared inputs ---
    for pattern, spec in adfs_model.items():
        # Find all user inputs that match this declared pattern
        matches = [k for k in adf_keys if re.fullmatch(pattern, k)]
        count = len(matches)

        if count < spec.min_occurs:
            raise ValueError(
                f"Missing adf matching pattern '{pattern}' — " f"found {count}, requires at least {spec.min_occurs}",
            )

        if spec.max_occurs is not None and count > spec.max_occurs:
            raise ValueError(
                f"Too many adfs matching pattern '{pattern}' — " f"found {count}, max allowed is {spec.max_occurs}",
            )


def _validate_adfs(adfs_model: Dict[str, AdfRegexSpec], adfs: "MappingAuxiliary") -> None:
    """

    Parameters
    ----------
    adfs_model
    adfs

    Returns
    -------

    """
    for adf_name, adf_value in adfs.items():
        matched = match_regex_key(adf_name, adfs_model)
        if not matched:
            raise ValueError(f"Unexpected adfs name '{adf_name}' — no declared regex matches it.")

    # --- Check for missing declared adfs ---
    for pattern, spec in adfs_model.items():
        # Find all user inputs that match this declared pattern
        matches = [k for k in adfs if re.fullmatch(pattern, k)]
        count = len(matches)

        if count < spec.min_occurs:
            raise ValueError(
                f"Missing adfs matching pattern '{pattern}' — " f"found {count}, requires at least {spec.min_occurs}",
            )


##################################
# Input validation sub functions
##################################


def _validate_inputs(
    input_model: Dict[str, "DataTypeModel"],
    inputs: "MappingDataType",
    validate_model: bool = False,
) -> None:
    """Validate user inputs against declared input model."""

    for user_key, value in inputs.items():
        pattern, spec = _get_pattern_and_spec(user_key, input_model)
        expected_type = _resolve_expected_type(spec)

        if _is_iterable_input(value, spec):
            # Based on _is_iterable we know it is an iterable of DataType
            _validate_iterable_input(user_key, cast(Iterable["DataType"], value), spec, expected_type, validate_model)
        else:
            _validate_single_input(user_key, value, spec, expected_type, validate_model)

    _validate_missing_inputs(input_model, inputs)


def _get_pattern_and_spec(user_key: str, input_model: Dict[str, "DataTypeModel"]) -> Tuple[str, "DataTypeModel"]:
    """
    Get the pattern and spec of a matched input in the model, raise if not found
    Parameters
    ----------
    user_key
    input_model

    Returns
    -------

    """
    matched = match_regex_key(user_key, input_model)
    if not matched:
        raise ValueError(f"Unexpected input name '{user_key}' — no declared regex matches it.")
    return matched


def _resolve_expected_type(spec: "DataTypeModel") -> type:
    """
    Get the expected type for the spec
    Parameters
    ----------
    spec

    Returns
    -------

    """
    return EOProduct if spec.type == "product" else EOContainer


def _is_iterable_input(value: Any, spec: "DataTypeModel") -> bool:
    return (
        spec.iterable_allowed
        and isinstance(value, Iterable)
        and not isinstance(value, (EOProduct, EOContainer, DataTree))
    )


def _validate_iterable_input(
    user_key: str,
    value: Iterable["DataType"],
    spec: "DataTypeModel",
    expected_type: type,
    validate_model: bool,
) -> None:
    """
    Validate an iterable input
    Parameters
    ----------
    user_key
    value
    spec
    expected_type
    validate_model

    Returns
    -------

    """
    count = 0
    for item in value:
        count += 1
        _validate_single_input(user_key, item, spec, expected_type, validate_model)

    if count < spec.min_occurs:
        raise ValueError(f"Input '{user_key}' requires at least {spec.min_occurs} elements")
    if spec.max_occurs is not None and count > spec.max_occurs:
        raise ValueError(f"Input '{user_key}' exceeds max_occurs={spec.max_occurs}")


def _validate_single_input(
    user_key: str,
    value: Any,
    spec: "DataTypeModel",
    expected_type: type,
    validate_model: bool,
) -> None:
    """

    Parameters
    ----------
    user_key
    value
    spec
    expected_type
    validate_model

    Returns
    -------

    """
    if not isinstance(value, expected_type):
        raise TypeError(f"Input '{user_key}' must be a single {expected_type.__name__}")
    if validate_model and isinstance(value, (EOProduct, EOContainer, DataTree)):
        _validate_data_type(spec.spec, user_key, value)


def _validate_missing_inputs(
    input_model: Dict[str, "DataTypeModel"],
    inputs: "MappingDataType",
) -> None:
    """
    Test for missing input in the input dict compared to the model list
    Parameters
    ----------
    input_model
    inputs

    Returns
    -------

    """
    for pattern, spec in input_model.items():
        matches = [k for k in inputs if re.fullmatch(pattern, k)]
        count = len(matches)

        if count < spec.min_occurs:
            raise ValueError(
                f"Missing inputs matching pattern '{pattern}' — " f"found {count}, requires at least {spec.min_occurs}",
            )
        if spec.max_occurs is not None and count > spec.max_occurs:
            raise ValueError(
                f"Too many inputs matching pattern '{pattern}' — " f"found {count}, max allowed is {spec.max_occurs}",
            )


##################################
# Input validation sub functions
##################################


def _validate_outputs(
    output_model: Dict[str, "DataTypeModel"],
    outputs: "MappingDataType",
    validate_model: bool = False,
) -> None:
    """Validate user outputs against declared output model."""

    for user_key, value in outputs.items():
        pattern, spec = _get_pattern_and_spec_output(user_key, output_model)
        expected_type = _resolve_expected_type(spec)

        if spec.iterable_allowed:
            _validate_iterable_output(user_key, value, spec, expected_type, validate_model)
        else:
            _validate_single_output(user_key, value, spec, expected_type, validate_model)

    _validate_missing_outputs(output_model, outputs)


def _get_pattern_and_spec_output(
    user_key: str,
    output_model: Dict[str, "DataTypeModel"],
) -> Tuple[str, "DataTypeModel"]:
    matched = match_regex_key(user_key, output_model)
    if not matched:
        raise ValueError(f"Unexpected output name '{user_key}' — no declared regex matches it.")
    return matched


def _validate_iterable_output(
    user_key: str,
    value: Any,
    spec: "DataTypeModel",
    expected_type: type,
    validate_model: bool,
) -> None:
    if not isinstance(value, Iterable) and not isinstance(value, (EOProduct, EOContainer, DataTree)):
        raise TypeError(f"Output '{user_key}' must be an iterable of {spec.type}s")

    for item in value:
        if not isinstance(item, expected_type):
            raise TypeError(f"Items in '{user_key}' must be of type {expected_type.__name__}")
        if validate_model and isinstance(item, (EOProduct, EOContainer, DataTree)):
            _validate_data_type(spec.spec, user_key, item)


def _validate_single_output(
    user_key: str,
    value: Any,
    spec: "DataTypeModel",
    expected_type: type,
    validate_model: bool,
) -> None:
    if not isinstance(value, expected_type):
        raise TypeError(f"Output '{user_key}' must be a single {expected_type.__name__}")
    if validate_model and isinstance(value, (EOProduct, EOContainer, DataTree)):
        _validate_data_type(spec.spec, user_key, value)


def _validate_missing_outputs(
    output_model: Dict[str, "DataTypeModel"],
    outputs: "MappingDataType",
) -> None:
    for pattern, spec in output_model.items():
        matches = [k for k in outputs if re.fullmatch(pattern, k)]
        count = len(matches)

        if count < spec.min_occurs:
            raise ValueError(
                f"Missing outputs matching pattern '{pattern}' — "
                f"found {count}, requires at least {spec.min_occurs}",
            )
        if spec.max_occurs is not None and count > spec.max_occurs:
            raise ValueError(
                f"Too many outputs matching pattern '{pattern}' — " f"found {count}, max allowed is {spec.max_occurs}",
            )


##################################
# Kwargs validation sub functions
##################################


def _validate_kwargs(attr_model: Dict[str, ParameterSpec], **kwargs: Any) -> None:
    """
    Ensures **kwargs match the mode's declared parameter specs.
    """

    # Check for unexpected kwargs
    for key in kwargs:
        if key in ["mode", "validate_mode"]:
            continue
        if key not in attr_model:
            raise ValueError(f"Unexpected parameter '{key}' for mode.")

    # Check for missing required params
    for key, spec in attr_model.items():
        if spec.required and key not in kwargs:
            raise ValueError(f"Missing required parameter '{key}'.")


##################################################
# Utility functions
##################################################
def match_regex_key(key: str, specs: Mapping[str, Any]) -> Optional[tuple[str, Any]]:
    """
    Try to find a (pattern, spec) in 'specs' whose regex matches 'key'.
    Returns (pattern, spec) or None if no match.
    """
    for pattern, spec in specs.items():
        if re.fullmatch(pattern, key):
            return pattern, spec
    return None


def _validate_data_type(
    model: EOProductModel | EOContainerModel,
    input_name: str,
    product: "DataType",
) -> None:
    """
    Validate that the datatype(product, container ...) validate it's model
    Parameters
    ----------

    product :  product datatype to validate
    input_name : input name for logging



    Returns
    -------

    """
    out_anom: list[AnomalyDescriptor] = []
    if isinstance(product, EOProduct):
        validate_product_against_model(
            model=cast(EOProductModel, model),
            product=product,
            mode="AT_LEAST",
            logger=EOLogging().get_logger("eopf.computing.processing_unit"),
            out_anomalies=out_anom,
        )
    elif isinstance(product, EOContainer):
        validate_container_against_model(
            model=cast(EOContainerModel, model),
            container=product,
            mode="AT_LEAST",
            logger=EOLogging().get_logger("eopf.computing.processing_unit"),
            out_anomalies=out_anom,
        )
    else:
        # Datatree not supported
        return
    if len(out_anom) != 0:
        logger = EOLogging().get_logger("eopf.computing.processing_unit")
        for anom in out_anom:
            logger.error(f"Anom : {anom.category} : {anom.description}")
        raise ValueError(
            f"Input product for '{input_name}' : '{product.name}' is not valid against schema",
        )


def get_mandatory_input_list(model: EOProcessingModel, mode: Optional[str] = None) -> list[str]:
    mode = regularize_mode(model, mode)
    mandatory_list = []
    for iname, ispec in model.modes_config[mode].inputs.items():
        if ispec.min_occurs > 0:
            mandatory_list.append(iname)
    return mandatory_list


def get_mandatory_adf_list(model: EOProcessingModel, mode: Optional[str] = None) -> list[str]:
    mode = regularize_mode(model, mode)
    mandatory_list: list[str] = []
    if model.modes_config[mode].adfs is None:
        return mandatory_list
    for iname, ispec in model.modes_config[mode].adfs.items():
        if ispec.min_occurs > 0:
            mandatory_list.append(iname)
    return mandatory_list


def get_provided_output_list(model: EOProcessingModel, mode: Optional[str] = None) -> list[str]:
    mode = regularize_mode(model, mode)
    mandatory_list: list[str] = []
    for iname, ispec in model.modes_config[mode].outputs.items():
        if ispec.min_occurs > 0:
            mandatory_list.append(iname)
    return mandatory_list


def regularize_mode(model: Optional[EOProcessingModel], mode: Optional[str]) -> str:
    if model is None:
        return "default" if mode is None else mode
    mode = model.default_mode if mode is None else mode
    if mode not in model.available_modes:
        modes_str = ", ".join(model.available_modes)
        raise KeyError(f"Not accepted mode : {mode} , possibles:  {modes_str}")
    return mode


#############################
# Tools
#############################


def get_model_from_params(
    inputs: "MappingDataType",
    mode: str,
    adfs: Optional["MappingAuxiliary"] = None,
    **kwargs: Any,
) -> "EOProcessingModel":
    input_models = _get_inputs_model_from_params(inputs)
    adfs_models: dict[str, AdfRegexSpec] = {}
    if adfs is not None:
        for k, i in adfs.items():
            adfs_models[k] = AdfRegexSpec(spec=AdfSpec())
    param_models: Dict[str, ParameterSpec] = {}
    for k, i in kwargs.items():
        if k == "validation_mode":
            continue
        param_models[k] = ParameterSpec()
    return EOProcessingModel(
        available_modes=[mode],
        default_mode=mode,
        modes_config={mode: ModeConfig(inputs=input_models, adfs=adfs_models, parameters=param_models)},
    )


def _get_inputs_model_from_params(
    inputs: "MappingDataType",
) -> dict[str, DataTypeModel]:
    input_models: dict[str, DataTypeModel] = {}
    for k, i in inputs.items():
        if isinstance(i, Iterable) and not isinstance(i, (EOProduct, EOContainer, DataTree)):
            for item in i:
                if isinstance(item, EOProduct):
                    input_models[k] = DataTypeModel(type="product", spec=product_to_model(item), iterable_allowed=True)
                elif isinstance(item, EOContainer):
                    input_models[k] = DataTypeModel(
                        type="container",
                        spec=container_to_model(item),
                        iterable_allowed=True,
                    )
                else:
                    raise ValueError("Only EOProduct or EOContainer allowed")
                break
        else:
            if isinstance(i, EOProduct):
                input_models[k] = DataTypeModel(type="product", spec=product_to_model(i))
            elif isinstance(i, EOContainer):
                input_models[k] = DataTypeModel(type="container", spec=container_to_model(i))
            else:
                raise ValueError("Only EOProduct or EOContainer allowed")
    return input_models
