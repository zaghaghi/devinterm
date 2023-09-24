from dataclasses import dataclass


@dataclass
class ServicePath:
    profile_name: str | None = None
    region_name: str | None = None
    service_name: str | None = None

    @property
    def completed(self) -> bool:
        return all([self.profile_name, self.region_name, self.service_name])

    @property
    def id(self) -> str:
        return f"{self.service_name}_{self.region_name}_{self.profile_name}"

    def clone(self) -> "ServicePath":
        return ServicePath(
            profile_name=self.profile_name,
            region_name=self.region_name,
            service_name=self.service_name,
        )
