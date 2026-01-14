import copy
import glob
import xml.etree.ElementTree as ET
from typing import Any, Dict, Iterable, List, Optional, TextIO, Tuple, Union

import numpy as np
import pandas as pd
import xmlschema
from defusedxml.ElementTree import fromstring, tostring
from pydantic import alias_generators

from eopf import EOContainer, EOGroup, EOLogging, EOProduct, EOVariable
from eopf.common.file_utils import AnyPath
from eopf.common.temp_utils import EOLocalTemporaryFolder
from eopf.store.mapping_manager import EOPFAbstractMappingManager, EOPreprocess
from eopf.store.safe import EOSafeFinalize

# mypy: disable-error-code="union-attr"

ANNOTATION_SCHEMA = "support/s1-level-1-product.xsd"


def to_snake_recursive(
    struct: dict[str, Any] | list[Any],
) -> dict[str, Any] | list[Any]:
    if isinstance(struct, dict):
        struct = {alias_generators.to_snake(k): to_snake_recursive(v) for k, v in struct.items()}
    elif isinstance(struct, list):
        struct = [to_snake_recursive(v) for v in struct]
    return struct


def fix_lists(struct: dict[str, Any] | list[Any]) -> dict[str, Any] | list[Any]:
    fixed = {}
    if isinstance(struct, dict):
        for k, v in struct.items():
            if k == "@count":
                continue
            if k[-5:] == "_list":
                try:
                    fixed[k] = fix_lists(struct[k][k[:-5]])
                except Exception:
                    fixed[k] = fix_lists(fix_lists(struct[k]))
            else:
                fixed[k] = fix_lists(struct[k])

    elif isinstance(struct, list):
        fixed = [fix_lists(v) for v in struct]  # type: ignore
    else:
        fixed = struct
    return fixed


def filter_metadata_dict(image_information: dict[str, Any] | list[Any]) -> dict[str, Any] | list[Any]:
    image_information = to_snake_recursive(image_information)
    image_information = fix_lists(image_information)
    return image_information


def parse_tag(
    xml_fp: TextIO,
    schema_path: str,
    query: str,
    validation: str = "skip",
) -> dict[str, Any]:
    schema = xmlschema.XMLSchema(schema_path)
    if hasattr(xml_fp, "seek"):
        xml_fp.seek(0)
    xml_tree = ET.parse(xml_fp)
    tag_dict: Any = schema.decode(xml_tree, query, validation=validation)
    return tag_dict


def parse_annotations(safe_path: str) -> Dict[str, Any]:
    schema = f"{safe_path}/{ANNOTATION_SCHEMA}"
    annotations = glob.glob(f"{safe_path}/annotation/*.xml")
    annotations_metadata = {}
    for annotation in annotations:
        with open(annotation, "r") as fp:
            quality_information = parse_tag(fp, schema, "qualityInformation")
            general_annotation = parse_tag(fp, schema, "generalAnnotation")
            image_information = parse_tag(fp, schema, "imageAnnotation")
            swath_merging = parse_tag(fp, schema, "swathMerging")
            swath_timing = parse_tag(fp, schema, "swathTiming")

        annotations_metadata.update(
            {
                annotation: {
                    "quality_information": filter_metadata_dict(quality_information),
                    "general_annotation": filter_metadata_dict(general_annotation),
                    "image_annotation": filter_metadata_dict(image_information),
                    "swath_timing": filter_metadata_dict(swath_timing),
                    "swath_merging": filter_metadata_dict(swath_merging),
                },
            },
        )
    return annotations_metadata


def reformat_other_metadata(other_metadata: Dict[str, Any], annotations_metadata: Dict[str, Any]) -> Dict[str, Any]:
    image_number = other_metadata["image_number"]
    for a in annotations_metadata:
        if a.endswith(f"-{image_number}.xml"):
            for meta in annotations_metadata[a]:
                other_metadata[meta] = annotations_metadata[a][meta]
    return other_metadata


def build_coordinates(additional_info: Dict[str, Any]) -> Tuple[Any, Any, Any, Any, Any]:
    """Build coordinates from metadata for Sentinel-1 products."""

    azimuth_time = pd.date_range(
        start=additional_info["product_first_line_utc_time"],
        end=additional_info["product_last_line_utc_time"],
        periods=additional_info["number_of_lines"],
    )
    pixel = np.arange(0, additional_info["number_of_samples"], dtype=int)
    line = np.arange(0, additional_info["number_of_lines"], dtype=int)
    ground_range = np.linspace(
        0,
        additional_info["range_pixel_spacing"] * (additional_info["number_of_samples"] - 1),
        additional_info["number_of_samples"],
    )
    slant_range_time = np.linspace(
        additional_info["image_slant_range_time"],
        additional_info["image_slant_range_time"]
        + (additional_info["number_of_samples"] - 1) / additional_info["range_sampling_rate"],
        additional_info["number_of_samples"],
    )
    return azimuth_time, pixel, line, ground_range, slant_range_time


def sanitize_quality_ground_range_coord(
    eoc: EOContainer,
    var_path: str,
    additional_info: Dict[Any, Any],
) -> None:
    var = eoc[var_path]
    if not isinstance(var, EOVariable):
        raise TypeError(f"There is no EOVariable at path {var_path}")
    pixel_indexes = var.data.coords["pixel"].isel(azimuth_time=0).values
    range_values = np.array([n * additional_info["range_pixel_spacing"] for n in pixel_indexes])
    coords = {
        "ground_range": ("ground_range", range_values),
        "pixel": ("ground_range", pixel_indexes),
    }
    eoc[var_path] = EOVariable(
        data=var.data.assign_coords(coords=coords),
        attrs=var.attrs,
    )


def sanitize_quality_slant_range_coord(
    eoc: EOContainer,
    var_path: str,
    additional_info: Dict[Any, Any],
) -> None:
    var = eoc[var_path]
    if not isinstance(var, EOVariable):
        raise TypeError(f"There is no EOVariable at path {var_path}")
    pixel_indexes = var.data.coords["pixel"].isel(azimuth_time=0).values
    range_values = np.array(
        [additional_info["image_slant_range_time"] + n / additional_info["range_sampling_rate"] for n in pixel_indexes],
    )
    coords = {
        "slant_range_time": ("slant_range_time", range_values),
        "pixel": ("slant_range_time", pixel_indexes),
    }
    eoc[var_path] = EOVariable(
        data=var.data.assign_coords(coords=coords),
        attrs=var.attrs,
    )


def prepare_noise_azimuth(product: Union[EOProduct, EOContainer]) -> None:
    noise_azimuth = product.quality.noise_azimuth.data.compute()
    noise_azimuth_lut_with_coords = noise_azimuth.noise_azimuth_lut.assign_coords(
        first_azimuth_time=noise_azimuth.first_azimuth_line,
        last_azimuth_time=noise_azimuth.last_azimuth_line,
        first_range_sample=noise_azimuth.first_range_sample,
        last_range_sample=noise_azimuth.last_range_sample,
    )
    product.quality["noise_azimuth"] = EOGroup(
        variables=dict(
            noise_azimuth_lut=EOVariable(
                data=noise_azimuth_lut_with_coords,
                attrs=noise_azimuth.noise_azimuth_lut.attrs,
            ),
        ),
        attrs=noise_azimuth.attrs,
    )


def compute_gcp_azimuth_time(azimuth_time: Any, line: int) -> np.datetime64:
    delta = azimuth_time.diff().mean()
    if line >= len(azimuth_time):
        azimuth_time_val = np.datetime64(azimuth_time[-1] + ((line - len(azimuth_time)) * delta), "ns")
    elif line < 0:
        azimuth_time_val = np.datetime64(azimuth_time[0] - ((line * delta)), "ns")
    else:  # 0 <= ggp["line"] < len(azimuth_time)
        azimuth_time_val = np.datetime64(azimuth_time[line], "ns")
    return azimuth_time_val


def compute_gcp_range_coord(additional_info: Dict[Any, Any], pixel: int, range_coord_name: str) -> Any:
    if "slant" in range_coord_name:
        range_coord_val = additional_info["image_slant_range_time"] + (pixel / additional_info["range_sampling_rate"])
    else:  # "ground" in range_coord_name
        range_coord_val = pixel * additional_info["range_pixel_spacing"]
    return range_coord_val


def build_gcp_variables(
    gcp: EOGroup,
    azimuth_time: Any,
    range_coord_name: str,
    additional_info: Dict[Any, Any],
) -> Iterable[Tuple[str, EOVariable]]:
    """
    Unstack dimensions in gcp group, in order to convert variables
    from 1D (grid_point) to 2D (azimuth_time, slant_range_time) for GRD.
    """

    geolocation_grid_points = _generate_geolocation_grid(gcp)

    azimuth_time_sel = []
    range_coord_sel = []
    line_set = set()
    pixel_set = set()

    for ggp in geolocation_grid_points:
        if ggp["line"] not in line_set:
            azimuth_time_sel.append(compute_gcp_azimuth_time(azimuth_time, ggp["line"]))
            line_set.add(ggp["line"])
        if ggp["pixel"] not in pixel_set:
            range_coord_sel.append(compute_gcp_range_coord(additional_info, ggp["pixel"], range_coord_name))
            pixel_set.add(ggp["pixel"])
    shape = (len(azimuth_time_sel), len(range_coord_sel))
    dims = ("azimuth_time", range_coord_name)
    data_vars = {
        "latitude": (dims, np.full(shape, np.nan), gcp.attrs),
        "longitude": (dims, np.full(shape, np.nan), gcp.attrs),
        "height": (dims, np.full(shape, np.nan), gcp.attrs),
        "incidence_angle": (dims, np.full(shape, np.nan), gcp.attrs),
        "elevation_angle": (dims, np.full(shape, np.nan), gcp.attrs),
        "azimuth_time_gcp": (dims, np.full(shape, np.nan), gcp.attrs),
        "slant_range_time_gcp": (dims, np.full(shape, np.nan), gcp.attrs),
    }
    line = sorted(line_set)
    pixel = sorted(pixel_set)
    for ggp in geolocation_grid_points:
        for var_name, var in data_vars.items():
            j = line.index(ggp["line"])
            i = pixel.index(ggp["pixel"])
            var[1][j, i] = ggp[var_name]
    for var_name, var in data_vars.items():  # cannot assign directly a Dataset to an EOGroup
        var1 = var[1].astype(ggp[var_name].dtype)
        eovar = EOVariable(
            data=var1,
            dims=dims,
        )
        yield (
            var_name,
            EOVariable(
                data=eovar.data.assign_coords(
                    {
                        "azimuth_time": [dt.astype("<M8[ns]") for dt in azimuth_time_sel],
                        range_coord_name: range_coord_sel,
                        "line": ("azimuth_time", line),
                        "pixel": (range_coord_name, pixel),
                    },
                ),
                attrs=gcp.attrs,
            ),
        )


def _generate_geolocation_grid(gcp: EOGroup) -> List[Dict[str, Any]]:
    # source: https://github.com/bopen/xarray-sentinel, xarray_sentinel/sentinel1.py#L227
    geolocation_grid_points: List[Dict[str, Any]] = [{} for _ in range(gcp.data.sizes["grid_point"])]
    for coord_name, coord_values in gcp.data.coords.items():
        for idx, v in enumerate(coord_values.values):
            geolocation_grid_points[idx].update({coord_name: v})
    for var_name, var_values in gcp.data.items():
        for idx, v in enumerate(var_values.values):
            geolocation_grid_points[idx].update({var_name: v})
    return geolocation_grid_points


def assign_degree_coord_to_doppler_centroid_vars(product: Union[EOProduct, EOContainer]) -> None:
    for var in ("data_dc_polynomial", "geometry_dc_polynomial"):
        if var in product.conditions.doppler_centroid:
            data_var = product.conditions.doppler_centroid[var]
            product.conditions.doppler_centroid[var] = EOVariable(
                data=data_var.data.assign_coords(
                    azimuth_time=("azimuth_time", data_var.data.azimuth_time.data),
                    degree=("degree", list(range(data_var.data.degree.size))[::-1]),
                ),
                attrs=data_var.attrs,
            )
            product.conditions.doppler_centroid[var].coords["azimuth_time"].attrs.update(
                data_var.data.azimuth_time.attrs,
            )
            product.conditions.doppler_centroid[var].coords["degree"].attrs.update(data_var.data.degree.attrs)


def assign_axis_coord_to_orbit_vars(product: Union[EOProduct, EOContainer]) -> None:
    for var in ("position", "velocity"):
        if var in product.conditions.orbit:
            data_var = product.conditions.orbit[var]
            product.conditions.orbit[var] = EOVariable(
                data=data_var.data.assign_coords(
                    azimuth_time=("azimuth_time", data_var.data.azimuth_time.data),
                    axis=("axis", ["x", "y", "z"]),
                ),
                attrs=data_var.attrs,
            )
            product.conditions.orbit[var].coords["azimuth_time"].attrs.update(data_var.data.azimuth_time.attrs)


def assign_range_coord_to_antena_pattern_vars(product: Union[EOProduct, EOContainer]) -> None:
    for var in ("slant_range_time_ap", "elevation_angle", "incidence_angle"):
        if var in product.conditions.antenna_pattern:
            data_var = product.conditions.antenna_pattern[var]
            product.conditions.antenna_pattern[var] = EOVariable(
                data=data_var.data.assign_coords(
                    azimuth_time=("azimuth_time", data_var.data.azimuth_time.data),
                    count=("count", list(range(data_var.data["count"].size))),
                ),
                attrs=data_var.attrs,
            )
            product.conditions.antenna_pattern[var].coords["count"].attrs.update(data_var.data["count"].attrs)
            product.conditions.antenna_pattern[var].coords["azimuth_time"].attrs.update(
                data_var.data.azimuth_time.attrs,
            )


class S01GRHSafeFinalize(EOSafeFinalize):
    """
    Finalize EOSafeStore import for Sentinel-1 GRD products.

    "finalize_function": {
           "class" : "S01GRHSafeFinalize"
       }
    """

    def finalize_product(
        self,
        eop: EOProduct,
        url: AnyPath,
        mapping: Optional[dict[str, Any]],
        mapping_manager: EOPFAbstractMappingManager,
        **eop_kwargs: Any,
    ) -> None:
        pass

    def finalize_container(
        self,
        container: EOContainer,
        url: AnyPath,
        mapping: Optional[dict[str, Any]],
        mapping_manager: EOPFAbstractMappingManager,
        **eop_kwargs: Any,
    ) -> None:
        annotations_metadata = parse_annotations(url.path)

        # procesing history should only be available at the product level
        processing_history = container.attrs.pop("processing_history", {})
        for _, product in container.items():

            additional_info = product.attrs.pop("additional_info")

            # duplicate and merge attributes into subproducts
            product_attrs = {
                "stac_discovery": container.attrs["stac_discovery"] | product.attrs.get("stac_discovery", {}),
                "other_metadata": container.attrs["other_metadata"] | product.attrs.get("other_metadata", {}),
                "processing_history": processing_history,
            }
            product.attrs.update(product_attrs)
            product.attrs["other_metadata"] = reformat_other_metadata(
                product_attrs["other_metadata"],
                annotations_metadata,
            )

            # build coordinates
            azimuth_time, pixel, line, ground_range, _ = build_coordinates(additional_info)

            # measurements/grd
            # There is no straightforward way to assign coordinates to existing variable,
            # so we have to recreate them. The EOVariable.assign_coords shortcut does not
            # operate inplace.
            # https://gitlab.eopf.copernicus.eu/cpm/eopf-cpm/-/issues/619
            data = product.measurements.grd.data.assign_coords(
                azimuth_time=("azimuth_time", azimuth_time),
                line=("azimuth_time", line),
                pixel=("ground_range", pixel),
                ground_range=("ground_range", ground_range),
            )
            chunk_sizes = {
                dim: chunk_size for dim, chunk_size in mapping.get("chunk_sizes", {}).items() if dim in data.coords
            }
            product.measurements["grd"] = EOVariable(
                data=data.chunk(chunk_sizes),
                attrs=product.measurements.grd.attrs,
            )

            # quality/noise_azimuth
            if "noise_azimuth" in product.quality:
                prepare_noise_azimuth(product)
            # quality/noise_range
            if "noise_range" in product.quality:
                sanitize_quality_ground_range_coord(product.quality.noise_range, "noise_range_lut", additional_info)
            # quality/calibration
            if "calibration" in product.quality:
                for var in product.quality.calibration:
                    sanitize_quality_ground_range_coord(product.quality.calibration, var, additional_info)

            assign_degree_coord_to_doppler_centroid_vars(product)
            assign_axis_coord_to_orbit_vars(product)
            assign_range_coord_to_antena_pattern_vars(product)

            # gcp
            for var_name, eovar in build_gcp_variables(
                product.conditions.gcp,
                azimuth_time,
                "ground_range",
                additional_info,
            ):
                product.conditions.gcp[var_name] = eovar


class S01OCNSafeFinalize(EOSafeFinalize):
    """
    Finalize EOSafeStore import for Sentinel-1 OCN products.

    "finalize_function": {
           "class" : "S01OCNSafeFinalize"
       }
    """

    def finalize_product(
        self,
        eop: EOProduct,
        url: AnyPath,
        mapping: Optional[dict[str, Any]],
        mapping_manager: EOPFAbstractMappingManager,
        **eop_kwargs: Any,
    ) -> None:

        pass

    def finalize_container(
        self,
        container: EOContainer,
        url: AnyPath,
        mapping: Optional[dict[str, Any]],
        mapping_manager: EOPFAbstractMappingManager,
        **eop_kwargs: Any,
    ) -> None:
        # procesing history should only be available at the product level
        processing_history = container.attrs.pop("processing_history", {})
        # duplicate and merge attributes into subproducts
        for _, category in container.items():
            for _, product in category.items():
                product_attrs = {
                    "stac_discovery": container.attrs["stac_discovery"] | product.attrs.get("stac_discovery", {}),
                    "other_metadata": container.attrs["other_metadata"] | product.attrs.get("other_metadata", {}),
                    "processing_history": processing_history,
                }
                product.attrs.update(product_attrs)


class S01SLCSafeFinalize(EOSafeFinalize):
    """
    Finalize EOSafeStore import for Sentinel-1 SLC products.

    "finalize_function": {
           "class" : "S01SLCSafeFinalize"
       }
    """

    def finalize_product(
        self,
        eop: EOProduct,
        url: AnyPath,
        mapping: Optional[dict[str, Any]],
        mapping_manager: EOPFAbstractMappingManager,
        **eop_kwargs: Any,
    ) -> None:

        pass

    def finalize_container(
        self,
        container: EOContainer,
        url: AnyPath,
        mapping: Optional[dict[str, Any]],
        mapping_manager: EOPFAbstractMappingManager,
        **eop_kwargs: Any,
    ) -> None:
        annotations_metadata = parse_annotations(url.path)

        # procesing history should only be available at the product level
        processing_history = container.attrs.pop("processing_history", {})
        for _, product in container.items():

            additional_info = product.attrs.pop("additional_info")

            # duplicate and merge attributes into subproducts
            product_attrs = {
                "stac_discovery": container.attrs["stac_discovery"] | product.attrs.get("stac_discovery", {}),
                "other_metadata": container.attrs["other_metadata"] | product.attrs.get("other_metadata", {}),
                "processing_history": processing_history,
            }
            product.attrs.update(product_attrs)
            product.attrs["other_metadata"] = reformat_other_metadata(
                product_attrs["other_metadata"],
                annotations_metadata,
            )

            # build coordinates
            azimuth_time, pixel, line, _, slant_range_time = build_coordinates(additional_info)

            # measurements/slc
            # There is no straightforward way to assign coordinates to existing variable,
            # so we have to recreate them. The EOVariable.assign_coords shortcut does not
            # operate inplace.
            # https://gitlab.eopf.copernicus.eu/cpm/eopf-cpm/-/issues/619
            data = product.measurements.slc.data.assign_coords(
                azimuth_time=("azimuth_time", azimuth_time),
                line=("azimuth_time", line),
                pixel=("slant_range_time", pixel),
                slant_range_time=("slant_range_time", slant_range_time),
            )
            chunk_sizes = {
                dim: chunk_size for dim, chunk_size in mapping.get("chunk_sizes", {}).items() if dim in data.coords
            }
            product.measurements["slc"] = EOVariable(
                data=data.chunk(chunk_sizes),
                attrs=product.measurements.slc.attrs,
            )

            # quality/noise_azimuth
            if "noise_azimuth" in product.quality:
                prepare_noise_azimuth(product)
            # quality/noise_range
            if "noise_range" in product.quality:
                sanitize_quality_slant_range_coord(product.quality.noise_range, "noise_range_lut", additional_info)

            # quality/calibration
            if "calibration" in product.quality:
                for var in product.quality.calibration:
                    sanitize_quality_slant_range_coord(product.quality.calibration, var, additional_info)

            assign_degree_coord_to_doppler_centroid_vars(product)
            assign_axis_coord_to_orbit_vars(product)
            assign_range_coord_to_antena_pattern_vars(product)

            # gcp
            for var_name, eovar in build_gcp_variables(
                product.conditions.gcp,
                azimuth_time,
                "slant_range_time",
                additional_info,
            ):
                product.conditions.gcp[var_name] = eovar


class S01SXWSLCSafeFinalize(S01SLCSafeFinalize):
    """
    Finalize EOSafeStore import for Sentinel-1 SLC TOPSAR products.

    "finalize_function": {
           "class" : "S01SXWSLCSafeFinalize"
       }
    """

    def finalize_product(
        self,
        eop: EOProduct,
        url: AnyPath,
        mapping: Optional[dict[str, Any]],
        mapping_manager: EOPFAbstractMappingManager,
        **eop_kwargs: Any,
    ) -> None:

        pass

    def finalize_container(
        self,
        container: EOContainer,
        url: AnyPath,
        mapping: Optional[dict[str, Any]],
        mapping_manager: EOPFAbstractMappingManager,
        **eop_kwargs: Any,
    ) -> None:

        super().finalize_container(
            container=container,
            url=url,
            mapping=mapping,
            mapping_manager=mapping_manager,
            **eop_kwargs,
        )

        # Extract the container data
        container_data = S01SXWSLCSafeFinalize._extract_container_data(container)

        # empty the eocontainer
        container_keys = list(container.keys())
        for product_name in container_keys:
            del container[product_name]

        # rebuild eocontainer
        for product_burst_name, product_burst_data in container_data.items():
            product = EOProduct(name=product_burst_name)
            product.attrs = product_burst_data["attributes"]
            for var_name, var in product_burst_data["measurements"].items():
                product[f"measurements/{var_name}"] = var
            for group_name, group in product_burst_data["conditions"].items():
                for var_name, var in group.items():
                    product[f"conditions/{group_name}/{var_name}"] = var
            for group_name, group in product_burst_data["quality"].items():
                for var_name, var in group.items():
                    product[f"quality/{group_name}/{var_name}"] = var
            container[product_burst_name] = product

    @staticmethod
    def _extract_container_data(container: EOContainer) -> Dict[str, Any]:
        """
        Extract the container data to further rebuild a new one
        Parameters
        ----------
        container

        Returns
        -------

        """
        logger = EOLogging().get_logger("eopf.s01.safe_finalizer")
        container_data = {}
        for product_name, product in container.items():

            # split into bursts
            burst_info = product.attrs["other_metadata"].pop("burst_info")

            burst_ids = burst_info.get("burst_id", list(range(len(burst_info))))
            burst_azimuth_times = burst_info["burst_azimuth_time"]

            for burst_idx, (burst_id, first_azimuth_time_burst) in enumerate(zip(burst_ids, burst_azimuth_times)):

                product_burst_name = f"{product_name}_{burst_id}"

                product_burst_attrs = copy.deepcopy(product.attrs)
                product_burst_attrs["other_metadata"]["burst_id"] = burst_id

                container_data[product_burst_name] = {
                    "attributes": product_burst_attrs,
                    "measurements": {},
                    "conditions": {},
                    "quality": {},
                }

                start_idx, end_idx = (
                    burst_info["lines_per_burst"] * burst_idx,
                    burst_info["lines_per_burst"] * (burst_idx + 1),
                )
                azimuth_time_burst = pd.date_range(
                    start=first_azimuth_time_burst,
                    periods=burst_info["lines_per_burst"],
                    freq=pd.Timedelta(burst_info["azimuth_time_interval"] * 10**9, unit="ns"),
                )

                for var_name, var in product.measurements.items():
                    splitted_data_var = var.data.isel(azimuth_time=slice(start_idx, end_idx))
                    splitted_data_var_retimed = splitted_data_var.assign_coords({"azimuth_time": azimuth_time_burst})
                    container_data[product_burst_name]["measurements"][var_name] = splitted_data_var_retimed

                for group_name, group in product.conditions.items():
                    container_data[product_burst_name]["conditions"].update({group_name: {}})
                    for var_name, var in group.items():
                        container_data[product_burst_name]["conditions"][group_name][var_name] = var.data

                first_valid_sample = EOVariable(
                    data=np.array(burst_info["first_valid_sample"][burst_idx].split(" "), dtype=int),
                    dims=("azimuth_time",),
                )
                last_valid_sample = EOVariable(
                    data=np.array(burst_info["last_valid_sample"][burst_idx].split(" "), dtype=int),
                    dims=("azimuth_time",),
                )

                first_valid_sample.assign_coords({"azimuth_time": azimuth_time_burst})
                last_valid_sample.assign_coords({"azimuth_time": azimuth_time_burst})
                container_data[product_burst_name]["conditions"]["burst_info"] = EOGroup(
                    variables=dict(
                        first_valid_sample=first_valid_sample.data,  # type: ignore
                        last_valid_sample=last_valid_sample.data,  # type: ignore
                    ),
                )

                for group_name, group in product.quality.items():
                    container_data[product_burst_name]["quality"].update({group_name: {}})
                    for var_name, var in group.items():
                        try:
                            container_data[product_burst_name]["quality"][group_name][var_name] = var.data
                        except TypeError as err:
                            # TODO
                            logger.error(f"quality/{group_name}/{var_name}\n : {err}")

        return container_data


class S01SL0_SafePreprocess(EOPreprocess):

    def __init__(self) -> None:

        XML_NAMESPACES = {
            "sdf": "http://www.gael.fr/2004/12/drb/sdf",
            "xs": "http://www.w3.org/2001/XMLSchema",
            "safe": "http://www.esa.int/safe/sentinel/1.1",
            "s0": "http://www.esa.int/safe/sentinel-1.0",
            "s1": "http://www.esa.int/safe/sentinel-1.0/sentinel-1",
            "s1sar": "http://www.esa.int/safe/sentinel-1.0/sentinel-1/sar",
            "xfdu": "urn:ccsds:schema:xfdu:1",
            "gml": "http://www.opengis.net/gml",
            "sentinel1": "http://www.esa.int/safe/sentinel/sentinel-1/1.0",
            "xsi": "http://www.w3.org/2001/XMLSchema-instance",
        }
        # update namespaces
        self._ET = ET
        for ns, path in XML_NAMESPACES.items():
            self._ET.register_namespace(ns, path)

    def _merge_data(self, merged_root: ET.Element, source_root: ET.Element) -> None:
        """Duplicate the entire xmlData block for general product information.

        This function creates a complete copy of the xmlData block from the source
        manifest and appends it to the generalProductInformation metadataWrap.

        Args:
            merged_root: Root element of the merged manifest
            source_root: Root element of the source manifest

        Note:
            Modifies merged_root in place by adding complete xmlData blocks

        <xfdu:XFDU xmlns:xfdu="urn:ccsds:schema:xfdu:1">
        <metadataSection>
            <metadataObject ID="generalProductInformation" classification="DESCRIPTION" category="DMD">
                <metadataWrap mimeType="text/xml" vocabularyName="SAFE">
                    <xmlData>
        """

        for bloc_path, children_name in [
            (".//metadataObject[@ID='generalProductInformation']/metadataWrap", "xmlData"),
            (".//metadataObject[@ID='processing']/metadataWrap", "xmlData"),
            (".//metadataObject[@ID='measurementQualityInformation']/metadataWrap", "xmlData"),
            ("./dataObjectSection", "dataObject"),
        ]:
            # Find the metadataWrap for generalProductInformation in merged manifest
            merged_bloc = merged_root.find(bloc_path)
            # Find the xmlData in source manifest
            source_bloc_children = source_root.findall(f"{bloc_path}/{children_name}")

            if merged_bloc and source_bloc_children:
                for source_bloc_child in source_bloc_children:
                    merged_bloc.append(source_bloc_child)

    def _merge_manifests(self, manifests: List[ET.ElementTree]) -> ET.ElementTree:
        """Merge multiple Sentinel-1 IW manifest files into a single one.

        This function combines multiple Sentinel-1 IW (Interferometric Wide swath) manifest files,
        typically representing different polarizations (e.g., HH, HV, VH, VV), into a unified
        manifest by duplicating entire xmlData blocks for each polarization.

        The merging strategy:
        - Uses the first manifest as the base structure
        - Duplicates complete xmlData blocks from additional manifests
        - Combines data objects from all manifests into shared sections
        - Preserves original IDs by working with complete xmlData duplications

        Args:
            *manifests: Variable number of manifest files as ElementTree objects.
                       First manifest is used as base, others are merged into it.

        Returns:
            ET.ElementTree: Merged manifest file as ElementTree containing
                           all elements from all input manifests

        Raises:
            ValueError: If no manifests provided or manifests have incompatible structure
        """
        if not manifests:
            raise ValueError("At least one manifest must be provided")

        # if len(manifests) == 1:
        #     return manifests[0]

        # Create a deep copy of the first manifest as the base
        merged = self._ET.ElementTree(fromstring(tostring(manifests[0].getroot())))
        merged_root = merged.getroot()

        # Process each additional manifest
        for manifest in manifests[1:]:
            manifest_root = manifest.getroot()

            # Duplicate entire xmlData blocks for different metadata objects
            if merged_root is None or manifest_root is None:
                pass
            else:
                self._merge_data(merged_root, manifest_root)

        return merged

    def run(
        self,
        url: AnyPath,
        **kwargs: Any,
    ) -> AnyPath:
        """

        Parameters
        ----------
        url : AnyPath, path to the product on disc
        kwargs : other kwargs passed to the load call in eop_kwargs

        Returns
        -------
        None
        """
        logger = EOLogging().get_logger("eopf.s01.l0.preprocessing")
        logger.info(f"Pre-processing START of S01 L0 product {url.path}")

        # make sure we have the product locally
        self._tmp_download_dir = url.get()
        if not url.islocal():
            logger.info(f"Downloading {url.path} to {self._tmp_download_dir.path}")
            # download the product locally if stored remote
            self._tmp_download_dir = url.get(recursive=True)
            logger.info("Downloading finished")
        else:
            self._tmp_download_dir = url

        # copy the contents of the inputs in a temporary folder
        # manifest are not copied since they need to be merged
        manifest_paths: List[AnyPath] = []
        self._tmp_dir = EOLocalTemporaryFolder().get()
        subpath = self._tmp_dir / url.basename
        logger.info(f"Creating local copy of {url.path} to {self._tmp_dir.path}")
        if subpath.exists():
            return subpath

        subpath.mkdir()
        for elem_path in self._tmp_download_dir.glob("/**/*"):
            # iterate over all downloaded products
            if elem_path.path.endswith("manifest.safe"):
                # manifest will not be moved directly
                # they will be merged
                manifest_paths.append(elem_path)
            else:
                # not manifest elements will be moved
                elem_path._fs.copy(elem_path.path, subpath.path, recursive=True)

        logger.info("Manifest merging")
        # run the manifest merge
        # even if we have one manifest file, as the mapping xml paths use namespaces added by merge script
        # retrieve the contents of all manifests
        parsed_manifests: List[ET.ElementTree] = []
        for manifest_path in manifest_paths:
            with manifest_path.open(mode="r") as manifest_fobj:
                parsed_manifest = self._ET.parse(manifest_fobj)
                parsed_manifests.append(parsed_manifest)  # type: ignore

        # merge the manifests
        merged_manifest = self._merge_manifests(parsed_manifests)

        # write the merged manifest on disk
        merged_manifest_path = subpath / "manifest.safe"
        with merged_manifest_path.open(mode="wb") as manifest_fobj:
            merged_manifest.write(manifest_fobj)

        # return the new working directory
        logger.info(f"Pre-processing END of S01 L0 product {url.path}")
        return subpath
