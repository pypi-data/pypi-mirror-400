from emtl.basics import get_available_dataset_ids, get_request_schema, clear_cache
from emtl.data import get_data_files
from emtl.custom_data_getters.wpuq import get_wpuq_weather_data

def dummy_data_dummy():

    # run: go to /data_loader/src and execute `python -m emt-dataloader._demo`
    clear_cache()

    all_dataset_ids = get_available_dataset_ids()
    print(all_dataset_ids)

    dataset_id = 'dummy_dataset'
    schema = get_request_schema(dataset_id)
    print(schema)

    request = schema.copy()
    request['request']['year'] = 2025
    data_file_paths = get_data_files(request)
    print(data_file_paths)


def wpuq_data_dummy():
    # run: go to /data_loader/src and execute `python -m emt-dataloader._demo`
    clear_cache()

    all_dataset_ids = get_available_dataset_ids()
    print(all_dataset_ids)

    dataset_id = 'wpuq'
    schema = get_request_schema(dataset_id)
    print(schema)

    request = schema.copy()
    _ = get_data_files(request)


if __name__ == "__main__":
    df = get_wpuq_weather_data(2020)
    print(df)

