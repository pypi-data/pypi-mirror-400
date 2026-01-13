import os


SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise OSError("SECRET_KEY environment variable is not set.")

BASE_URL = os.getenv("BASE_URL", "https://dev-cmsdials-api.web.cern.ch/")
TEST_WORKSPACE = os.getenv("TEST_WORKSPACE", "global")
TEST_DATASET_ID = int(os.getenv("TEST_DATASET_ID", 15310647))  # /ZeroBias/Run2025B-PromptReco-v1/DQMIO
TEST_FILE_ID = int(
    os.getenv("TEST_FILE_ID", 22961052797)
)  # /store/data/Run2025B/ZeroBias/DQMIO/PromptReco-v1/000/392/158/00000/DC769215-780F-4D7D-B0B7-E66F731E3FC0.root
TEST_RUN_NUMBER = int(os.getenv("TEST_RUN_NUMBER", 392158))
TEST_LS_NUMBER = int(os.getenv("TEST_LS_NUMBER", 10))
