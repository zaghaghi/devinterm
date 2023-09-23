from functools import partial

import boto3
from textual.command import Hit, Hits, Provider
from textual.message import Message


class RegionCommands(Provider):
    class Selected(Message):
        def __init__(self, region_name: str) -> None:
            self.region_name = region_name
            super().__init__()

    def get_available_regions(self) -> list[str]:
        return boto3.Session().get_available_regions("s3")

    async def startup(self) -> None:
        worker = self.app.run_worker(self.get_available_regions, thread=True)
        self._regions = await worker.wait()

    async def search(self, query: str) -> Hits:
        matcher = self.matcher(query)
        max_match = 5
        for region in self._regions:
            command = f"region {region}"
            score = matcher.match(command)
            if score > 0:
                yield Hit(
                    score,
                    matcher.highlight(command),
                    partial(self.select_region, region),
                    help=f"Change AWS region to {region}",
                )
                max_match -= 1
            if max_match <= 0:
                break

    def select_region(self, region_name: str) -> None:
        self.screen.post_message(self.Selected(region_name))
