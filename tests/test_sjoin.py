import pytest

import geopandas
from geopandas.testing import assert_geodataframe_equal

import dask_geopandas


@pytest.mark.parametrize(
    "npartitions_left, npartitions_right", [(4, 4), (1, 3), (3, 1), (3, 4)]
)
def test_sjoin_dask_geopandas(npartitions_left, npartitions_right):
    df_points = geopandas.read_file(geopandas.datasets.get_path("naturalearth_cities"))
    ddf_points = dask_geopandas.from_geopandas(df_points, npartitions=npartitions_left)

    df_polygons = geopandas.read_file(
        geopandas.datasets.get_path("naturalearth_lowres")
    )
    ddf_polygons = dask_geopandas.from_geopandas(
        df_polygons, npartitions=npartitions_right
    )

    expected = geopandas.sjoin(df_points, df_polygons, op="within", how="inner")
    expected = expected.sort_index()

    # dask / geopandas
    result = dask_geopandas.sjoin(ddf_points, df_polygons, op="within", how="inner")
    assert_geodataframe_equal(expected, result.compute().sort_index())

    # geopandas / dask
    result = dask_geopandas.sjoin(df_points, ddf_polygons, op="within", how="inner")
    assert_geodataframe_equal(expected, result.compute().sort_index())

    # dask / dask
    result = dask_geopandas.sjoin(ddf_points, ddf_polygons, op="within", how="inner")
    assert_geodataframe_equal(expected, result.compute().sort_index())

    # with spatial_partitions
    ddf_points.calculate_spatial_partitions()
    ddf_polygons.calculate_spatial_partitions()
    result = dask_geopandas.sjoin(ddf_points, ddf_polygons, op="within", how="inner")
    assert result.spatial_partitions is not None
    assert_geodataframe_equal(expected, result.compute().sort_index())
