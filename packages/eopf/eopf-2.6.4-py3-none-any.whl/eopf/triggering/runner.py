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
runner.py

Workflow runner

"""
import importlib
import os
import sys
import time
from abc import ABC
from contextlib import nullcontext
from dataclasses import dataclass
from typing import Any, List, Optional, Union
from warnings import warn

import dask.config
from dotenv import load_dotenv

from eopf import EOConfiguration, __version__
from eopf.common import file_utils
from eopf.common.env_utils import resolve_env_vars
from eopf.common.file_utils import AnyPath
from eopf.common.functions_utils import change_working_dir
from eopf.common.temp_utils import EOTemporaryFolder
from eopf.dask_utils import DaskContext
from eopf.dask_utils.dask_helpers import is_worker_reachable
from eopf.exceptions.errors import TriggerInvalidWorkflow
from eopf.logging import EOLogging
from eopf.triggering.interfaces import (
    EOBreakPointParserResult,
    EOExternalModuleImportParserResult,
    EOIOParserResult,
    EOQCTriggeringConf,
)
from eopf.triggering.parsers import (
    BreakPointSection,
    ConfigFilesSection,
    DaskContextSection,
    EnvVarsSection,
    EOIOSection,
    ExternalModulesSection,
    GeneralConfigurationSection,
    LoggingFilesSection,
    QualityControlSection,
    SecretSection,
    WorkflowSection,
    load_section,
)
from eopf.triggering.workflow import EOProcessorWorkFlow

EOConfiguration().register_requested_parameter(
    "triggering__validate_run",
    False,
    description="validate outputs of units",
)
EOConfiguration().register_requested_parameter(
    "triggering__validate_mode",
    "STRUCTURE",
    description="Validation mode, python Flags : STRUCTURE | STAC, NONE, MODEL | STAC, FULL ( full validation)",
)
EOConfiguration().register_requested_parameter(
    "triggering__use_default_filename",
    True,
    description="Use default filename when using folder outputs, else use product.name",
)
EOConfiguration().register_requested_parameter(
    "triggering__use_basic_logging",
    False,
    description="Setup a basic logging",
)
EOConfiguration().register_requested_parameter(
    "triggering__load_default_logging",
    False,
    description="Load the default logging configuration from cpm",
)
EOConfiguration().register_requested_parameter(
    "triggering__wait_before_exit",
    0,
    description="Wait N seconds at end of processing to analyze dask dashboard",
)
EOConfiguration().register_requested_parameter(
    "triggering__dask_monitor__enabled",
    True,
    description="Activate dask cluster monitoring",
)
EOConfiguration().register_requested_parameter(
    "triggering__dask_monitor__cancel",
    True,
    description="Allows to cancel all dask computation when error detected on monitor",
)
EOConfiguration().register_requested_parameter(
    "triggering__dask_monitor__cancel_state",
    "PAUSED | STUCK_SPILL",
    description="Allows to cancel all dask computation when error detected on monitor",
)
EOConfiguration().register_requested_parameter(
    "triggering__use_datatree",
    False,
    description="Use Datatree as product type in processor unit",
)

EOConfiguration().register_requested_parameter(
    "triggering__use_datatree_xarray",
    True,
    description="Use xarray.open_datatree directly to open dtree, otherwise iterate on zarr groups",
)


EOConfiguration().register_requested_parameter(
    "triggering__error_policy",
    "FAIL_FAST",
    description="Error handling policy : default to exit at first error",
)

EOConfiguration().register_requested_parameter(
    "triggering__create_temporary",
    True,
    description="Create a temporary folder if not already setup as EOTemporaryFolder singleton",
)

EOConfiguration().register_requested_parameter(
    "triggering__clean_temporary",
    default_value=True,
    description="Clean the temporary folder created by triggering",
)

EOConfiguration().register_requested_parameter(
    "triggering__temporary_shared",
    False,
    description="Ensure that the temporary folder is reachable from all the dask worker",
)


@dataclass
class ParsersResults:
    """
    Dataclass holding the overall parsers results
    """

    breakpoints: Optional[EOBreakPointParserResult]
    general_config: dict[str, Any]
    processing_workflow: EOProcessorWorkFlow
    io_config: EOIOParserResult
    dask_context: DaskContext | nullcontext[None]
    logging_config: list[str]
    config: list[str]
    secret_files: list[str]
    eoqc_config: Optional[EOQCTriggeringConf]


class EORunner(ABC):
    """EORunner class implement workflow execution from a given payload"""

    def __init__(self) -> None:
        self.logger = EOLogging().get_logger("eopf.triggering.runner")
        self.eotemp_trigger_created: bool = False

    def run_from_file(
        self,
        payload_file: Union[AnyPath, str],
        working_dir: Optional[Union[AnyPath, str]] = None,
    ) -> None:
        """

        Parameters
        ----------
        working_dir : optional working dir
        payload_file : yaml payload file

        Returns
        -------
        None

        """
        payload_dir = AnyPath.cast(payload_file).dirname()
        working_dir = AnyPath.cast(working_dir) if working_dir is not None else payload_dir
        payload = file_utils.load_yaml_file(payload_file)
        with change_working_dir(working_dir):
            self.run(payload)

    def run(self, payload: dict[str, Any]) -> None:
        """Generic method that apply the algorithm of the processing unit
        from the payload and write the result product.

        Parameters
        ----------
        payload: dict[str, Any]
            dict of metadata to find and run the processing unit, create the output product
            and write it.
        """

        self.logger.debug(f" >> {EORunner.run.__qualname__}")
        self.logger.info(f"CPM Version {__version__}")
        parsers_results = self.extract_from_payload_and_init_conf_logging(payload)
        # Create the temporary folder if needed
        self._create_temporary()

        # Dask/Null context manager instance
        dask_context = parsers_results.dask_context

        with dask_context as dc:
            if isinstance(dask_context, DaskContext):
                self.logger.info(f"Dask context : {dask_context}")
                if dask_context.client is not None:
                    self.logger.info(f"Dask dashboard can be reached at : {dask_context.client.dashboard_link}")
            else:
                dask_scheduler_type = (
                    scheduler_type if (scheduler_type := dask.base.get_scheduler()) is not None else "threads"
                )
                self.logger.info(f"No dask distributed, using default dask scheduler {dask_scheduler_type}")

            parsers_results.processing_workflow.run_workflow(parsers_results.io_config, dc, parsers_results.eoqc_config)

            # Wait to let the user check the local dask dashboard
            self.logger.info(f"Sleeping for {EOConfiguration().triggering__wait_before_exit}s")
            if isinstance(dask_context, DaskContext) and dask_context.client is not None:
                self.logger.info(f"Dask dashboard can be reached at : {dask_context.client.dashboard_link}")
            time.sleep(EOConfiguration().triggering__wait_before_exit)
            # cleanup temp dir if any and has been created by triggering
            self._clean_temporary()

    def _clean_temporary(self) -> None:
        if (
            EOTemporaryFolder.is_instantiated()
            and self.eotemp_trigger_created
            and EOConfiguration().get("triggering__clean_temporary", True)
        ):
            self.logger.info(f"Cleaning up temporary folder in : {EOTemporaryFolder().get()}")
            EOTemporaryFolder().cleanup()
            EOTemporaryFolder.clear()

    def _create_temporary(self) -> None:
        # Temporary dictionary ?
        if EOConfiguration().get("triggering__create_temporary", True):
            self.eotemp_trigger_created = False
            if not EOTemporaryFolder.is_instantiated():
                self.eotemp_trigger_created = True
            temp_dir = EOTemporaryFolder(
                dont_clean=bool(EOConfiguration().get("triggering__clean_temporary", True)),
            ).get()
            if EOConfiguration().get("triggering__temporary_shared", False):
                if not is_worker_reachable(temp_dir):
                    raise TriggerInvalidWorkflow(f"Temporary folder {temp_dir} is not reachable from the workers !!!!")

    def extract_from_payload_and_init_conf_logging(self, payload: dict[str, Any]) -> ParsersResults:
        """Retrieve all the information from the given payload

        the payload should have this keys:

            * 'workflow': describe the processing workflow to run
            * 'breakpoints': configure workflow element as breakpoint
            * 'I/O': configure Input/Output element
            * 'dask_context': configure dask scheduler and execution
            * 'logging': configure logging ( optional)
            * 'config' : configure all (optional)

        See :ref:`triggering-usage`

        Parameters
        ----------
        payload: dict[str, Any]

        Returns
        -------
        tuple:
            All component corresponding to the metadata
        """
        # Path the I/O
        if "I/O" in payload:
            warn("Use io instead of I/O", DeprecationWarning)
            payload["io"] = payload.pop("I/O")

        # First search for dotenv in payload
        dotenvs = load_section(payload, EnvVarsSection).dotenv
        for a in dotenvs:
            a.make_absolute()
        self._load_dotenvs(dotenvs)

        # resolve all env_vars in the payload
        payload = resolve_env_vars(payload)
        # Clear loaded configuration not to pollute the env
        EOConfiguration().clear_loaded_configurations()

        # load the config
        config = load_section(payload, ConfigFilesSection).config
        # register the provided configuration files
        for conf in config:
            EOConfiguration().load_file(conf.make_absolute().path)
        # secrets
        secret_files = load_section(payload, SecretSection).secret
        # register the provided secret files
        for sec in secret_files:
            EOConfiguration().load_secret_file(sec.make_absolute().path)
        # load the general config
        general_config = load_section(payload, GeneralConfigurationSection).general_configuration
        EOConfiguration().load_dict(general_config)

        # basic config ?
        if EOConfiguration().get("triggering__use_basic_logging", False):
            EOLogging.setup_basic_config()
        # then load the logging
        logging_config = load_section(payload, LoggingFilesSection).logging
        if EOConfiguration().get("triggering__load_default_logging", default=False):
            EOLogging().enable_default_conf()
        # register the provided logging_config
        for log_conf in logging_config:
            EOLogging().register_cfg(
                os.path.splitext(os.path.basename(log_conf.path))[0],
                log_conf.make_absolute().path,
            )
        # Additional imports
        additional_imported_modules: List[EOExternalModuleImportParserResult] = load_section(
            payload,
            ExternalModulesSection,
        ).external_modules
        self.import_external_modules([a.make_absolute() for a in additional_imported_modules])
        # Breakpoint activation
        breakpoints = load_section(payload, BreakPointSection).breakpoints
        EORunner.activate_breakpoints(breakpoints)
        # Load the other elements ( breakpoints, workflow, I/O)

        # Worflow stuff
        dask_context = load_section(payload, DaskContextSection).dask_context
        io_config = load_section(payload, EOIOSection).io

        processing_workflow = load_section(payload, WorkflowSection).workflow
        eoqc_config = load_section(payload, QualityControlSection).eoqc

        return ParsersResults(
            breakpoints=breakpoints,
            general_config=general_config,
            processing_workflow=processing_workflow,
            io_config=io_config,
            dask_context=dask_context,
            logging_config=logging_config,
            config=config,
            secret_files=secret_files,
            eoqc_config=eoqc_config.make_absolute() if eoqc_config is not None else None,
        )

    def _load_dotenvs(self, dotenvs: list[AnyPath]) -> None:
        # register the provided env files
        for envfile in dotenvs:
            if not AnyPath.cast(envfile).exists():
                raise TriggerInvalidWorkflow(f"{envfile} doesn't exists !!!")
            self.logger.info(f"Loading {envfile} into env vars")
            load_dotenv(
                envfile.path,
            )

    @staticmethod
    def activate_breakpoints(io_breakpoint: EOBreakPointParserResult | None) -> None:
        """
        Activate the corresponding breakpoints. If all or ALL in the list activate ALL breakpoints in the code
        Parameters
        ----------
        io_breakpoint : breakpoints data coming from parser

        Returns
        -------

        """
        if io_breakpoint is None:
            return
        io_breakpoint.make_absolute()

        if io_breakpoint.all:
            EOConfiguration()["breakpoints__activate_all"] = True
            return
        for brkp in io_breakpoint.ids:
            EOConfiguration()[f"breakpoints__{brkp}"] = True
        if io_breakpoint.folder is not None:
            EOConfiguration()["breakpoints__folder"] = io_breakpoint.folder
        if io_breakpoint.store_params is not None:
            EOConfiguration()["breakpoints__storage_options"] = io_breakpoint.store_params

    def import_external_modules(self, module_list: list[EOExternalModuleImportParserResult]) -> None:
        """
        Import external modules
        Parameters
        ----------
        module_list : list of modules to load

        Returns
        -------

        """
        global_dict = globals()
        for module in module_list:
            module_name = module.name
            try:
                # add folder to sys.path if provided
                if module.folder is not None:

                    # Convert to absolute string path
                    import_path = AnyPath.cast(module.folder).absolute

                    # Add to sys.path if not already present
                    if import_path not in sys.path:
                        self.logger.info(f"Adding {import_path} to sys.path for imports")
                        sys.path.insert(0, import_path.path)

                # Determine the name to use in the global namespace
                module_name_in_globals = module.alias if module.alias else module.name
                imported_module = importlib.import_module(module_name)
                global_dict[module_name_in_globals] = imported_module
                self.logger.info(f"Module {module_name} loaded successfully as {module_name_in_globals}")
                if module.nested:
                    # Optionally, you can also inject specific attributes of the module
                    for attribute_name in dir(imported_module):
                        # don't load private attr
                        if not attribute_name.startswith("_"):
                            global_dict[attribute_name] = getattr(imported_module, attribute_name)
            except ModuleNotFoundError as err:
                raise TriggerInvalidWorkflow(f"Module {module_name} not found") from err
