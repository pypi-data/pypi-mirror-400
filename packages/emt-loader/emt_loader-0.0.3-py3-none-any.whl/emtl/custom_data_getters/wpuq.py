import pandas as pd

from emtl.basics import get_request_schema
from emtl.data import get_data_files, delete_files


TEMPORAL_RESOLUTIONS = ['10s', '1min', '15min', '60min']
YEARS = list(range(2018, 2021))
DATASET_ID = 'wpuq'


def print_wpuq_description():
    """Print the general information of the WPuQ dataset."""

    schema = get_request_schema(DATASET_ID)
    print(schema['description'])


def get_wpuq_household_load_data(year: int, temporal_resolution: str,
                                 only_pv: bool = False, only_no_pv: bool = False,
                                 cache: bool = True) -> pd.DataFrame:
    """
    Get all WPuQ household load data for the given year and temporal resolution.
    Loads household load data for all available WITH_PV and NO_PV single family households.
    """
    return _get_wpuq_load_data('HOUSEHOLD', year, temporal_resolution,
                               only_pv=only_pv, only_no_pv=only_no_pv, cache=cache)


def get_wpuq_heatpump_load_data(year: int, temporal_resolution: str,
                                only_pv: bool = False, only_no_pv: bool = False,
                                cache: bool = True) -> pd.DataFrame:
    """
    Get all WPuQ heatpump load data for the given year and temporal resolution.
    Loads heatpump load data for all available WITH_PV and NO_PV single family households.
    """
    return _get_wpuq_load_data('HEATPUMP', year, temporal_resolution,
                               only_pv=only_pv, only_no_pv=only_no_pv, cache=cache)


def _get_wpuq_load_data(load_key: str, year: int, temporal_resolution: str,
                        only_pv: bool = False, only_no_pv: bool = False,
                        cache: bool = True) -> pd.DataFrame:
    """
    Get all WPuQ heatpump load data for the given year and temporal resolution.
    Loads heatpump load data for all available WITH_PV and NO_PV single family households.
    """

    # param checking
    if only_pv and only_no_pv:
        raise ValueError('error: only_pv and only_no_pv cannot be True simultaneously.')
    if temporal_resolution not in TEMPORAL_RESOLUTIONS:
        raise ValueError(f'error: temporal_resolution must be one of {TEMPORAL_RESOLUTIONS}.')
    if year not in YEARS:
        raise ValueError(
            f'error: year must between {YEARS[0]} and {YEARS[-1]} (inclusive).')
    # build request schema
    request_schema = get_request_schema(DATASET_ID)
    request_schema['request']['year'] = year
    request_schema['request']['file_name'] = f'data_{temporal_resolution}'
    request_schema['request']['top_level_nodes'] = ['WITH_PV'] if only_pv else ['WITH_NO_PV'] if only_no_pv else ['WITH_PV', 'WITH_NO_PV']
    request_schema['request']['mid_level_nodes'] = []  # all nodes
    request_schema['request']['low_level_nodes'] = load_key.capitalize()
    # fetch and concat data
    data_file_paths = get_data_files(request_schema)
    data_dfs = [pd.read_csv(f) for f in data_file_paths]
    return pd.concat(data_dfs, axis=0, ignore_index=True)


def get_wpuq_weather_data(year: int, cache: bool = True) -> pd.DataFrame:
    """
    todo
    """
    # param checking
    if year not in YEARS:
        raise ValueError(
            f'error: year must between {YEARS[0]} and {YEARS[-1]} (inclusive).')
    # build request schema
    request_schema = get_request_schema(DATASET_ID)
    request_schema['request']['year'] = year
    request_schema['request']['file_name'] = 'weather'
    request_schema['request']['top_level_nodes'] = ['WEATHER_SERVICE']
    request_schema['request']['mid_level_nodes'] = ['IN']
    request_schema['request']['low_level_nodes'] = ['WEATHER_TEMPERATURE_TOTAL']
    # fetch and concat data
    data_file_paths = get_data_files(request_schema)
    data_dfs = [pd.read_csv(f) for f in data_file_paths]
    if not cache:
        delete_files(data_file_paths)
    return pd.concat(data_dfs, axis=0, ignore_index=True)
