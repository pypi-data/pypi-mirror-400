import pandas as pd
from urllib3.util import Retry

from cmsdials.clients.h2d.models import LumisectionHistogram2D, PaginatedLumisectionHistogram2DList
from cmsdials.filters import LumisectionHistogram2DFilters

from .env import TEST_DATASET_ID, TEST_LS_NUMBER, TEST_RUN_NUMBER
from .utils import setup_dials_object


def test_get_h2d() -> None:
    dials = setup_dials_object()

    # Fetch any valid monitoring element ID with dimension 2 from the MEs endpoint
    data = dials.mes.list()
    me_id = None
    for me in data:
        if me.dim == 2:
            me_id = me.me_id
            break
    assert me_id is not None, "No 2D Monitoring Element found in MEs endpoint"

    data = dials.h2d.get(dataset_id=TEST_DATASET_ID, run_number=TEST_RUN_NUMBER, ls_number=TEST_LS_NUMBER, me_id=me_id)
    assert isinstance(data, LumisectionHistogram2D)


def test_list_h2d() -> None:
    dials = setup_dials_object()
    data = dials.h2d.list()
    assert isinstance(data, PaginatedLumisectionHistogram2DList)
    assert isinstance(data.to_pandas(), pd.DataFrame)


def test_list_all_h2d() -> None:
    dials = setup_dials_object()
    data = dials.h2d.list_all(LumisectionHistogram2DFilters(), max_pages=5)
    assert isinstance(data, PaginatedLumisectionHistogram2DList)
    assert isinstance(data.to_pandas(), pd.DataFrame)


def test_get_h2d_with_retries() -> None:
    dials = setup_dials_object()

    # Fetch any valid monitoring element ID with dimension 2 from the MEs endpoint
    data = dials.mes.list()
    me_id = None
    for me in data:
        if me.dim == 2:
            me_id = me.me_id
            break
    assert me_id is not None, "No 2D Monitoring Element found in MEs endpoint"

    data = dials.h2d.get(
        dataset_id=TEST_DATASET_ID,
        run_number=TEST_RUN_NUMBER,
        ls_number=TEST_LS_NUMBER,
        me_id=me_id,
        retries=Retry(total=3, backoff_factor=0.1),
    )
    assert isinstance(data, LumisectionHistogram2D)


def test_list_h2d_with_retries() -> None:
    dials = setup_dials_object()
    data = dials.h2d.list(retries=Retry(total=3, backoff_factor=0.1))
    assert isinstance(data, PaginatedLumisectionHistogram2DList)
    assert isinstance(data.to_pandas(), pd.DataFrame)


def test_list_all_h2d_with_retries() -> None:
    dials = setup_dials_object()
    data = dials.h2d.list_all(LumisectionHistogram2DFilters(), max_pages=5, retries=Retry(total=5, backoff_factor=0.1))
    assert isinstance(data, PaginatedLumisectionHistogram2DList)
    assert isinstance(data.to_pandas(), pd.DataFrame)
