import logging
import os
import pathlib
import shutil
import tempfile

TEST_DIR = tempfile.mkdtemp(prefix="tsm_tests")


class TSMTestCase:
    """
    Copied and modified from `https://github.com/allenai/allennlp/blob/main/allennlp/common/testing/test_case.py`.
    """

    PROJECT_ROOT = (pathlib.Path(__file__).parent / "..").resolve()
    MODULE_ROOT = PROJECT_ROOT / "tsm"
    TESTS_ROOT = PROJECT_ROOT / "tests"
    FIXTURES_ROOT = PROJECT_ROOT / "test_fixtures"

    def setup_method(self):
        logging.basicConfig(
            format="%(asctime)s - %(levelname)s - %(name)s - %(message)s", level=logging.DEBUG
        )
        # Disabling some of the more verbose logging statements that typically aren't very helpful
        # in tests.
        #logging.getLogger("tsm.g2p").setLevel(logging.INFO)
        self.TEST_DIR = pathlib.Path(TEST_DIR)

        os.makedirs(self.TEST_DIR, exist_ok=True)

    def teardown_method(self):
        shutil.rmtree(self.TEST_DIR)
