import time

from loguru import logger

from bb_integrations_lib.gravitate.testing.util import generate_model_validation_tests, \
    generate_pydantic_models_from_open_api


class TestBuilder:
    def __init__(self,
                 client: str,
                 system: str):
        self.client = client
        self.system = system

    @property
    def models_file_path(self):
        return f"./{self.client}/{self.system}/models.py"

    @property
    def tests_file_path(self):
        return f"./{self.client}/{self.system}/tests/test_models.py"

    @property
    def open_api_url(self):
        urls = {
            "sd": f"https:/{self.client}.bb.gravitate.energy/api/openapi.json/internal",
            "rita": "https://rita.gravitate.energy/api/openapi.json"
        }
        return urls[self.system]

    def build_tests(self):
        try:
            generate_pydantic_models_from_open_api(
                open_api_url=self.open_api_url,
                save_file_to_path=self.models_file_path
            )
            time.sleep(1)
            generate_model_validation_tests(
                models_file_path=self.models_file_path,
                tests_file_path=self.tests_file_path
            )
        except Exception as e:
            logger.error(f"Failed to build tests: {e}")
            raise

    @classmethod
    def for_client_and_system(cls, client: str, system: str):
        instance = cls(client=client, system=system)
        instance.build_tests()
        return instance


if __name__ == "__main__":
    test_builder = TestBuilder.for_client_and_system("tte", "sd")
