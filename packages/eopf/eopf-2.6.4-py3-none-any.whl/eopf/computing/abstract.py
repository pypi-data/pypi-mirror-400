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
abstract.py

Abstract classes definition for the computing module

"""
import inspect
import os.path
import warnings
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, List, Mapping, Optional, Type, TypeAlias, Union

from xarray.core.datatree import DataTree

import eopf
from eopf import EOConfiguration, EOContainer
from eopf.common import date_utils, file_utils, history_utils
from eopf.common.file_utils import AnyPath, load_json_file
from eopf.common.functions_utils import camel_to_snake
from eopf.computing.validation import (
    EOProcessingModel,
    get_mandatory_adf_list,
    get_mandatory_input_list,
    get_provided_output_list,
    regularize_mode,
    validate_output_models,
    validate_run_parameters,
)
from eopf.exceptions.errors import (
    EOComputeBadConfigurationError,
)
from eopf.product import EOProduct
from eopf.product.eo_validation import ValidationMode

DataType: TypeAlias = Union[EOProduct, EOContainer, DataTree]
MappingDataType: TypeAlias = Mapping[str, DataType | Iterable[DataType]]

EOConfiguration().register_requested_parameter(
    "processing_facility",
    param_is_optional=True,
    description="Processing facility to put in history",
)


@dataclass
class AuxiliaryDataFile:
    """
    AuxiliaryDataFile

    dataclass holding an ADF definition

    """

    name: str
    path: AnyPath
    store_params: Optional[dict[str, Any]] = None
    # Data pointer to store opened data or whatever you wants
    data_ptr: Any = None

    def __post_init__(self) -> None:
        # Force Anypath, if path is already Anypath does nothing
        self.path = AnyPath.cast(self.path)

    def __repr__(self) -> str:
        """
        string repr
        Returns
        -------

        """
        return f"ADF {self.name} : {self.path} : {self.data_ptr}"


ADF: TypeAlias = AuxiliaryDataFile
MappingAuxiliary: TypeAlias = Mapping[str, AuxiliaryDataFile]


class EOProcessingBase(ABC):
    """
    Define base functionalities for all processing elements such as identifier and representation
    """

    @property
    def identifier(self) -> Any:
        """Identifier of the processing step"""
        return self._identifier

    def __init__(self, identifier: Any = ""):
        self._identifier = identifier or str(id(self))

    def __str__(self) -> str:
        return f"{self.__class__.__name__}<{self.identifier}>"

    def __repr__(self) -> str:
        return f"[{id(self)}]{str(self)}"


class EOProcessingStep(EOProcessingBase):
    """Converts one or several input arrays (of one or several variables)
    into one array (of one intermediate or output variable).

    These algorithms should be usable outside a Dask context to allow re-use in other
    software or integration of existing algorithms.


    Parameters
    ----------
    identifier: str, optional
        a string to identify this processing step (useful for logging)

    See Also
    --------
    dask.array.Array
    """

    def __init__(self, identifier: Any = ""):
        warnings.warn("Deprecated, we no longer enforce the use of ProcessingSteps", DeprecationWarning)
        super().__init__(identifier)

    @abstractmethod
    def apply(self, *inputs: Any, **kwargs: Any) -> Any:  # pragma: no cover
        """Abstract method that is applied for one block of the inputs.

        It creates a new array from arrays, can be any accepted type by map_block function from Dask.

        Parameters
        ----------
        *inputs: any
            input arrays (numpy, xarray) with same number of chunks each compatible with map_block functions
        **kwargs: any
            any needed kwargs

        Returns
        -------
        Any : same kind as the input type ( numpy array or xarray DataArray)
        """


def _load_processing_model(cls: Type[Any], processor_name: str, processor_version: str) -> EOProcessingModel:
    if not processor_name and not processor_version:
        raise ValueError("PROCESSOR_NAME and PROCESSOR_VERSION can't be empty")

    model_file_path = AnyPath(
        os.path.join(
            Path(inspect.getfile(cls)).parent,
            "models",
            camel_to_snake(processor_name)
            + ("_" if len(processor_name) != 0 else "")
            + camel_to_snake(processor_version)
            + ".json",
        ),
    )

    if model_file_path.exists():
        data = load_json_file(model_file_path)
        return EOProcessingModel(**data)

    raise KeyError(f"No computing model file found under {model_file_path}")


class EOProcessingUnit(EOProcessingBase):
    """Abstract base class of processors i.e. processing units
    that provide valid EOProducts with coordinates etc.

    Parameters
    ----------
    identifier: str, optional
        a string to identify this processing unit (useful for logging and tracing)

    See Also
    --------
    eopf.product.EOProduct
    """

    # To be overloaded if needed
    PROCESSOR_NAME = ""
    PROCESSOR_VERSION = ""
    PROCESSOR_LEVEL = ""
    PROCESSOR_MODEL = True
    _processing_model: Optional[EOProcessingModel] = None

    def __init_subclass__(cls) -> None:
        super().__init_subclass__()
        if cls.PROCESSOR_NAME and cls.PROCESSOR_VERSION and cls.PROCESSOR_MODEL:
            cls._processing_model = _load_processing_model(cls, cls.PROCESSOR_NAME, cls.PROCESSOR_VERSION)

    def __init__(self, identifier: Any = "") -> None:
        super().__init__(identifier)
        # Flag to update history of output product or not
        # To be updated in subclass to define if the processor is supposed to update
        self._update_history = False
        # Additional infos to add in history.
        # See https://cpm.pages.eopf.copernicus.eu/eopf-cpm/main/PSFD/7-metadata.html#processing-history
        self._additional_history: dict[str, Any] = {}
        # Load a default configuration is any
        self._load_default_configuration()

    @classmethod
    def processing_model(cls) -> Optional[EOProcessingModel]:
        return cls._processing_model

    @classmethod
    def get_available_modes(cls) -> List[str]:
        """
        Get the list of available mode for the processor

        Returns
        -------
        The list of processor's mode
        """
        processing_model = cls.processing_model()
        if processing_model is None:
            return ["default"]
        return processing_model.available_modes

    @classmethod
    def get_default_mode(cls) -> str:
        """
        Get the default mode of the processor

        Returns
        -------
        The default processor mode
        """
        processing_model = cls.processing_model()
        if processing_model is None:
            return "default"
        return processing_model.default_mode

    @classmethod
    def get_tasktable_description(cls, mode: Optional[str] = None, **kwargs: Any) -> Mapping[str, Any]:
        """
        Return the tasktable description for the Processing unit
        Parameters
        ----------
        mode : Optional str to specify the processing mode, if not provided default mode given
        kwargs : Any deciding parameter accepted by the processor get_tasktable_description ( see processor's doc)

        Returns
        -------
        Dictionary describing the tasktable
        """
        mode = regularize_mode(cls.processing_model(), mode)
        tasktable_file_path = AnyPath(
            os.path.join(
                Path(inspect.getfile(cls)).parent,
                "tasktables",
                camel_to_snake(cls.PROCESSOR_NAME) + ("_" if len(cls.PROCESSOR_NAME) != 0 else "") + mode + ".json",
            ),
        )
        if tasktable_file_path.exists():
            return file_utils.load_json_file(tasktable_file_path)
        raise KeyError(f"No tasktable file found for {mode} in {tasktable_file_path}")

    @classmethod
    def _load_default_configuration(cls, mode: Optional[str] = None, **kwargs: Any) -> None:
        """
        Get the configuration file installed if any and load it
        Parameters
        ----------
        mode : Optional str to specify the processing mode, if not provided default mode given
        kwargs : Any deciding parameter accepted by the processor get_tasktable_description ( see processor's doc)

        Returns
        -------
        Dictionary describing the tasktable
        """
        mode = regularize_mode(cls.processing_model(), mode)

        try:
            source_file_path = inspect.getfile(cls)
        except TypeError:
            return
        except OSError:
            return
        conf_file_path = AnyPath(
            os.path.join(
                Path(source_file_path).parent,
                "config",
                camel_to_snake(cls.PROCESSOR_NAME) + ("_" if len(cls.PROCESSOR_NAME) != 0 else "") + mode + ".toml",
            ),
        )
        if conf_file_path.exists() and conf_file_path.islocal():
            EOConfiguration().load_file(conf_file_path.path)

    @classmethod
    def get_mandatory_input_list(cls, mode: Optional[str] = None, **kwargs: Any) -> list[str]:
        """
        Get the list of mandatory inputs names regexes to be provided for the run method.
        In some cases, this list might depend on parameters and ADFs.
        If parameters are not provided, default behaviour is to provide the minimal list.
        Note: This method does not verify the content of the products, it only provides the list.

        Parameters
        ----------
        mode: mode to select
        kwargs : same parameters as for the run method if available

        Returns
        -------
        the list of mandatory products to be provided
        """
        processing_model = cls.processing_model()
        if processing_model is None:
            return []
        return get_mandatory_input_list(processing_model, mode)

    @classmethod
    def get_mandatory_adf_list(cls, mode: Optional[str] = None, **kwargs: Any) -> list[str]:
        """
        Get the list of mandatory ADF input names to be provided for the run method.
        In some cases, this list might depend on parameters.
        If parameters are not provided, default behaviour is to provide the minimal list.
        Note: This method does not verify the content of the ADF, it only provides the list.
        So no check on input ADF can be performed here.

        Parameters
        ----------
        mode: mode to select
        kwargs : same parameters as for the run method if available

        Returns
        -------
        the list of mandatory ADFs to be provided
        """
        processing_model = cls.processing_model()
        if processing_model is None:
            return []
        return get_mandatory_adf_list(processing_model, mode)

    @classmethod
    def get_provided_output_list(cls, mode: Optional[str] = None, **kwargs: Any) -> list[str]:
        """
        Get the list of provided outputs for a given mode and params

        Parameters
        ----------
        mode: mode to select
        kwargs : same parameters as for the run method if available

        Returns
        -------
        the list of products provided

        """
        processing_model = cls.processing_model()
        if processing_model is None:
            return []
        return get_provided_output_list(processing_model, mode)

    @abstractmethod
    def run(
        self,
        inputs: MappingDataType,
        adfs: Optional[MappingAuxiliary] = None,
        mode: Optional[str] = None,
        **kwargs: Any,
    ) -> MappingDataType:  # pragma: no cover
        """
        Abstract method to provide an interface for algorithm implementation

        Warn : Should not be used in production as it doesn't validate anything

        Parameters
        ----------
        inputs: Mapping[str,DataType]
            all the products to process in this processing unit
        adfs: Optional[Mapping[str,AuxiliaryDataFile]]
            all the ADFs needed to process
        mode: mode to select

        **kwargs: any
            any needed kwargs (e.g. parameters)

        Returns
        -------
        Mapping[str, DataType ]
        """

    def run_validating(
        self,
        inputs: MappingDataType,
        adfs: Optional[MappingAuxiliary] = None,
        mode: Optional[str] = None,
        validation_mode: ValidationMode = ValidationMode.STRUCTURE,
        **kwargs: Any,
    ) -> MappingDataType:
        """Transforms input products into a new valid EOProduct/EOContainer/DataTree with new variables.

        Parameters
        ----------
        inputs: dict[str,DataType]
            all the products to process in this processing unit
        adfs: Optional[dict[str,AuxiliaryDataFile]]
            all the ADFs needed to process
        mode: mode to select
        validation_mode: AllowedValidationMode
            Mode to validate see eo_product_validation

        **kwargs: any
            any needed kwargs

        Returns
        -------
        dict[str, DataType]
        """
        mode = regularize_mode(self.processing_model(), mode)
        # verify that the parameters are valid to run
        processing_model = self.processing_model()
        if processing_model is not None:
            validate_run_parameters(processing_model, inputs, mode, adfs, **kwargs, validate_model=True)

        if adfs is not None:
            result_products = self.run(inputs, adfs, mode=mode, **kwargs)
        else:
            result_products = self.run(inputs, mode=mode, **kwargs)
        self._add_history_event(inputs=inputs, outputs=result_products, adfs=adfs, mode=mode, **kwargs)
        if processing_model is not None:
            validate_output_models(processing_model, result_products, mode, validate_model=True)
        self._validate_products(result_products, validation_mode)
        return result_products

    def _add_history_event(
        self,
        inputs: MappingDataType,
        outputs: MappingDataType,
        mode: str,
        adfs: Optional[MappingAuxiliary] = None,
        **kwargs: Any,
    ) -> None:
        if not self._update_history:
            return

        if self.PROCESSOR_VERSION == "" or self.PROCESSOR_NAME == "" or self.PROCESSOR_LEVEL == "":
            raise EOComputeBadConfigurationError(
                "Processor is either missing version, name or processor level to create history",
            )

        # Build adf list
        adf_list = None
        if adfs is not None:
            adf_list = []
            for adf in adfs.values():
                adf_list.append(adf.name)

        # build input list
        input_list = build_id_list(inputs)

        # build output list
        output_list = build_id_list(outputs)

        new_history_entry = {
            "processor": self.PROCESSOR_NAME,
            "version": self.PROCESSOR_VERSION,
            "facility": EOConfiguration()["processing_facility"],
            "time": date_utils.get_utc_str_now(),
            "inputs": input_list,
            "outputs": output_list,
            "eopf_cpm_version": eopf.__version__,
            **self._additional_history,
        }
        if adf_list:
            new_history_entry["adfs"] = adf_list
        new_history_entry["execution_parameters"] = {"mode": mode, **kwargs}
        status, message = history_utils.check_history_entry(new_history_entry)
        if not status:
            raise EOComputeBadConfigurationError(f"History event is not valid : {message}")

        self.__add_history_event_to_outputs(new_history_entry, outputs)

    def __add_history_event_to_outputs(self, new_history_entry: dict[str, Any], outputs: MappingDataType) -> None:
        """
        Add this history event to all the sub outputs

        Parameters
        ----------
        new_history_entry : event to add
        outputs : outputs to add the event to

        Returns
        -------
        None
        """
        for output_ptr in outputs.values():
            # output_ptr is a list of products
            if isinstance(output_ptr, Iterable) and not isinstance(output_ptr, (EOProduct, EOContainer, DataTree)):
                for sub_output in output_ptr:
                    if isinstance(sub_output, (EOProduct, EOContainer)):
                        history_utils.extend_history(sub_output, new_history_entry, self.PROCESSOR_LEVEL)
                    else:
                        raise ValueError("Can't handle history for non EOProduct/EOContainer types")
            elif isinstance(output_ptr, (EOProduct, EOContainer)):
                history_utils.extend_history(output_ptr, new_history_entry, self.PROCESSOR_LEVEL)
            else:
                raise ValueError("Can't handle history for non EOProduct/EOContainer types")

    def _validate_products(self, products: MappingDataType, validation_mode: ValidationMode) -> None:
        """Verify that the given product is valid.

        If the product is invalid, raise an exception.

        See Also
        --------
        eopf.product.EOProduct.validate
        """
        for p in products.items():
            # input is a list of products
            if isinstance(p, Iterable) and not isinstance(p, (EOProduct, EOContainer, DataTree)):
                for pp in p:
                    if isinstance(pp, (EOProduct, EOContainer)):
                        pp.validate(validation_mode)
            elif isinstance(p[1], (EOProduct, EOContainer)):
                p[1].validate(validation_mode)


def build_id_list(mapping_data: MappingDataType) -> List[str]:
    """
    Extract the list of ids of the given MappingDataType,
    Goes through the iterables also

    Parameters
    ----------
    mapping_data

    Returns
    -------

    """
    id_list = []
    for input_ptr in mapping_data.values():
        # input_ptr is a list of products
        if isinstance(input_ptr, Iterable) and not isinstance(input_ptr, (EOProduct, EOContainer, DataTree)):
            for sub_input in input_ptr:
                if isinstance(sub_input, (EOProduct, EOContainer)):
                    id_list.append(sub_input.attrs["stac_discovery"]["id"])
                else:
                    raise ValueError("Can't handle id for non EOProduct/EOContainer types")
        elif isinstance(input_ptr, (EOProduct, EOContainer)):
            id_list.append(input_ptr.attrs["stac_discovery"]["id"])
        else:
            raise ValueError("Can't handle id for non EOProduct/EOContainer types")
    return id_list
