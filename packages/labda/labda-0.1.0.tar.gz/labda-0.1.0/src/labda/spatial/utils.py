import geopandas as gpd


def remove_invalid_geometries(gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """Remove invalid geometries from the GeoDataFrame."""
    return gdf[~gdf.geometry.isna() & ~gdf.geometry.is_empty]


def check_crs_unit(gdf: gpd.GeoDataFrame | gpd.GeoSeries, unit: str) -> None:
    if gdf.crs is not None:
        if gdf.crs.axis_info[0].unit_name != unit:
            raise ValueError(
                f"The CRS of the GeoDataFrame must have a unit of '{unit}'."
            )
    else:
        raise ValueError("The GeoDataFrame must have a CRS defined.")
