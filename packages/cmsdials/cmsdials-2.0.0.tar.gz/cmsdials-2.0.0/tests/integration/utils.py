from cmsdials import Dials
from cmsdials.auth.secret_key import Credentials

from .env import BASE_URL, SECRET_KEY, TEST_WORKSPACE


def setup_dials_object() -> Dials:
    creds = Credentials(token=SECRET_KEY)
    return Dials(creds, base_url=BASE_URL, workspace=TEST_WORKSPACE)
