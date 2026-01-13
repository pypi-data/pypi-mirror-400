from ...utils.api_client import BaseAuthorizedNonPaginatedAPIClient
from .models import MEFilters, MonitoringElement


class MonitoringElementClient(
    BaseAuthorizedNonPaginatedAPIClient[
        MonitoringElement,
        MEFilters,
    ]
):
    data_model = MonitoringElement
    filter_class = MEFilters
    lookup_url = "mes/"

    def get(self, id: int, **kwargs):  # noqa: A002
        edp = f"{id}/"
        return super()._get(edp, **kwargs)
