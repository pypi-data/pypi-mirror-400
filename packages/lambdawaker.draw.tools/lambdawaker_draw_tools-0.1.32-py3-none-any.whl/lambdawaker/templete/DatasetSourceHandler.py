from lambdawaker.templete.process_data_payload import process_data_payload


class DataSetResourceHandler:
    match_pattern = "lw.ds://**"

    def __init__(self, dataset_sources: list):
        self.data_sources_dict = {
            data_sources.id.lower(): data_sources for data_sources in dataset_sources
        }

    def __getitem__(self, item):
        path = item.split("/")
        if len(path) <= 2:
            return self.data_sources_dict[item.lower()]
        else:
            ds_id = "/".join(path[:2])
            record_path = "/".join(path[2:])
            ds = self.data_sources_dict[ds_id.lower()]
            return ds[record_path]

    def __call__(self, route, request):
        cleaned_url = request.url.replace("lw.ds://", "")

        split = cleaned_url.split("/")
        dataset_id = "/".join(split[:2]).lower()
        resource_path = "/".join(split[2:])

        dataset = self.data_sources_dict.get(dataset_id, None)

        if dataset is None:
            print(f"> Dataset not found: {dataset_id}")
            route.continue_()
            return

        data = dataset[resource_path]

        content_type, file_data = process_data_payload(data)

        if content_type is None:
            print(f"> File not found: {cleaned_url}")
            route.continue_()
            return

        route.fulfill(
            status=200,
            content_type=content_type,
            body=file_data
        )
