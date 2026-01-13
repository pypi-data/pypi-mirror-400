from playwright.sync_api import sync_playwright

from lambdawaker.templete.DatasetSourceHandler import DataSetResourceHandler
from lambdawaker.templete.LocalResourcesHandler import DiskResourceHandler


class PlaywrightRenderer:
    def __init__(self, dataset_sources: list):
        self.playwright = sync_playwright().start()

        self.browser = self.playwright.chromium.launch()
        page = self.browser.new_page()

        disk_resource_handler = DiskResourceHandler()
        data_source_handler = DataSetResourceHandler(dataset_sources)
        handlers = [disk_resource_handler, data_source_handler]

        for handler in handlers or []:
            page.route(handler.match_pattern, handler)

        self.page = page
        self.data_source_handler = data_source_handler

    def stop(self):
        self.playwright.stop()
