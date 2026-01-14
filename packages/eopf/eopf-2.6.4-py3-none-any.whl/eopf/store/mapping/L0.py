import copy
from typing import Any, Optional

from eopf import EOContainer, EOLogging, EOProduct
from eopf.common.file_utils import AnyPath
from eopf.store.mapping_manager import EOPFAbstractMappingManager
from eopf.store.safe import EOSafeFinalize

logger = EOLogging().get_logger(__name__)


def recursive_complete_dict(
    d1: dict[str, Any],
    d2: dict[str, Any],
) -> None:
    """
    Recursively updates dictionary `d1` with values from `d2`,
    allowing separate modes for handling dictionaries, lists, and sets.
    """
    for key, value in d2.items():
        if key in d1:
            if key in (
                "other_metadata",
                "stac_discovery",
                "properties",
                "processing_history",
            ):
                recursive_complete_dict(d1[key], copy.copy(value))
            elif d1[key] != value:
                logger.debug(f"attrs value differ between top EOContainer ({d1[key]!r}) and EOProduct {value!r}")
        else:
            d1[key] = copy.deepcopy(value)  # Add new keys from d2


def recursive_copy_attrs_to_products(eoboject: EOContainer | EOProduct, reference_dict: dict[Any, Any]) -> None:
    """
    Recursively copies attributes from `reference_dict` to `eoboject`.

    This function traverses through `eoboject` (which can be an `EOContainer` or `EOProduct`).
    If `eoboject` is an `EOContainer`, it recursively processes each child.
    If `eoboject` is an `EOProduct`, it updates its attributes using `recursive_complete_dict`.

    Args:
        eoboject (EOContainer | EOProduct): The object to update.
    """
    if isinstance(eoboject, EOContainer):
        recursive_complete_dict(eoboject.attrs, reference_dict)
        for child in eoboject.values():
            recursive_copy_attrs_to_products(child, reference_dict)
    elif isinstance(eoboject, EOProduct):
        recursive_complete_dict(eoboject.attrs, reference_dict)


class L0GenericSafeFinalize(EOSafeFinalize):
    """
    This finalizer copy top container attrs to sub container or products recursively.
    If an attribute is already present in children, we do not replace it because we consider it has been set voluntary
    before, for example by mapping.
    Exception for processing_history, stac_discovery, other_metadata and properties: in this case, we complete dicts
    with new values.
    """

    def finalize_container(
        self,
        container: EOContainer,
        url: AnyPath,
        mapping: Optional[dict[str, Any]],
        mapping_manager: EOPFAbstractMappingManager,
        **eop_kwargs: Any,
    ) -> None:
        """
        Finalizes the container.

        :param container: EOContainer to be finalized
        :param url: File path or remote location of the data file
        :param mapping: Optional mapping dictionary for auxiliary operations
        :param mapping_manager: Instance of EOPFAbstractMappingManager to handle
            metadata mappings
        :param eop_kwargs: Additional keyword arguments
        """
        recursive_copy_attrs_to_products(container, copy.deepcopy(container.attrs))

    def finalize_product(
        self,
        eop: EOProduct,
        url: AnyPath,
        mapping: Optional[dict[str, Any]],
        mapping_manager: EOPFAbstractMappingManager,
        **eop_kwargs: Any,
    ) -> None:
        """
        Finalizes the eoproduct.

        :param eop: eoproduct to be finalized
        :param url: File path or remote location of the data file
        :param mapping: Optional mapping dictionary for auxiliary operations
        :param mapping_manager: Instance of EOPFAbstractMappingManager to handle
            metadata mappings
        :param eop_kwargs: Additional keyword arguments
        """
        return None
