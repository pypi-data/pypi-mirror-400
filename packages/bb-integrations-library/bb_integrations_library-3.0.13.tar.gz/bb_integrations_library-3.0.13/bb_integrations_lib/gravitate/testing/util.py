import importlib.util
import inspect
import json
from pathlib import Path
from typing import get_origin, Union, get_args, Any, Dict
import time
from datamodel_code_generator import generate, DataModelType, InputFileType
from loguru import logger
from pydantic import BaseModel

from bb_integrations_lib.gravitate.testing.openapi import get_updated_supply_and_dispatch_openapi_json


def ensure_directory_exists(file_path: Path) -> None:
    """Ensure the parent directory of a file path exists."""
    file_path.parent.mkdir(parents=True, exist_ok=True)
    return None


def generate_pydantic_models_from_open_api(open_api_url: str,
                                           save_file_to_path: str,
                                           schemas_to_include: list[str] = None,
                                           open_api_json: dict = None) -> None:
    try:
        openapi_data = open_api_json or get_updated_supply_and_dispatch_openapi_json(
            open_api_url,
            schemas_to_include or ['V1', 'V2'])
        if isinstance(openapi_data, str):
            try:
                openapi_json = json.loads(openapi_data)
                logger.info("Parsed OpenAPI JSON string to dictionary")
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse OpenAPI JSON string: {e}")
                raise
        else:
            openapi_json = openapi_data
        if not isinstance(openapi_json, dict):
            raise ValueError(f"Expected dict or JSON string, got {type(openapi_json)}")
        save_path = Path(save_file_to_path)
        temp_openapi_file = save_path.parent / "temp_openapi.json"
        ensure_directory_exists(save_path)
        ensure_directory_exists(temp_openapi_file)
        with open(temp_openapi_file, 'w') as f:
            json.dump(openapi_json, f, indent=2)
        generate(
            input_=temp_openapi_file,
            output=save_path,
            output_model_type=DataModelType.PydanticV2BaseModel
        )
        if temp_openapi_file.exists():
            temp_openapi_file.unlink()
        logger.info(f"Successfully generated Pydantic models at {save_file_to_path}")
    except Exception as e:
        logger.error(f"Error generating pydantic models: {e}")
        temp_openapi_file = Path(save_file_to_path).parent / "temp_openapi.json"
        if temp_openapi_file.exists():
            temp_openapi_file.unlink()
        raise
    return None


def generate_model_validation_tests(models_file_path: str, tests_file_path: str) -> None:
    """Generate validation tests for all Pydantic models in the models file."""
    try:
        if not Path(models_file_path).exists():
            logger.error(f"Models file does not exist: {models_file_path}")
            return
        models = load_pydantic_models_from_file(models_file_path)
        if not models:
            logger.warning(f"No Pydantic models found in {models_file_path}")
            return
        test_data = {}
        for model_name, model_class in models.items():
            try:
                example_input = generate_example_input(model_class)
                test_data[model_name] = example_input
            except Exception as e:
                logger.warning(f"Could not generate example for {model_name}: {e}")
                test_data[model_name] = {}
        create_test_file(tests_file_path, models_file_path, test_data)

        logger.info(f"Generated validation tests for {len(models)} models in {tests_file_path}")

    except Exception as e:
        logger.error(f"Error generating model validation tests: {e}")
        raise


def load_pydantic_models_from_file(file_path: str) -> Dict[str, BaseModel]:
    models = {}
    try:
        spec = importlib.util.spec_from_file_location("models", file_path)
        if spec is None or spec.loader is None:
            logger.error(f"Could not load module spec from {file_path}")
            return models

        models_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(models_module)
        for name in dir(models_module):
            try:
                obj = getattr(models_module, name)
                if (inspect.isclass(obj) and
                        issubclass(obj, BaseModel) and
                        obj is not BaseModel):
                    models[name] = obj
            except Exception as e:
                logger.debug(f"Skipping {name}: {e}")
                continue

    except Exception as e:
        logger.error(f"Error loading models from {file_path}: {e}")

    return models


def generate_example_input(model_class: BaseModel) -> Dict[str, Any]:
    example = {}
    try:
        if hasattr(model_class, 'model_fields'):
            fields = model_class.model_fields
            for field_name, field_info in fields.items():
                try:
                    example[field_name] = generate_field_example(field_info.annotation, field_name)
                except Exception as e:
                    logger.debug(f"Could not generate example for field {field_name}: {e}")
                    example[field_name] = f"example_{field_name}"
        elif hasattr(model_class, '__fields__'):
            fields = model_class.__fields__
            for field_name, field_info in fields.items():
                try:
                    example[field_name] = generate_field_example(field_info.type_, field_name)
                except Exception as e:
                    logger.debug(f"Could not generate example for field {field_name}: {e}")
                    example[field_name] = f"example_{field_name}"
        else:
            logger.warning(f"Could not find fields for model {model_class.__name__}")
    except Exception as e:
        logger.warning(f"Error generating example input for {model_class.__name__}: {e}")

    return example


def generate_field_example(field_type: Any, field_name: str) -> Any:
    """Generate example value for a field type."""
    try:
        origin = get_origin(field_type)
        args = get_args(field_type)
        if origin is Union:
            non_none_types = [arg for arg in args if arg is not type(None)]
            if non_none_types:
                field_type = non_none_types[0]
        if origin is list:
            if args:
                item_type = args[0]
                return [generate_field_example(item_type, f"{field_name}_item")]
            return ["example_item"]
        if origin is dict:
            return {"key": "value"}
        if field_type == str:
            return f"example_{field_name}"
        elif field_type == int:
            return 42
        elif field_type == float:
            return 3.14
        elif field_type == bool:
            return True
        elif field_type == list:
            return ["example_item"]
        elif field_type == dict:
            return {"key": "value"}
        else:
            return f"example_{field_name}"
    except Exception as e:
        logger.debug(f"Error generating field example for {field_name}: {e}")
        return f"example_{field_name}"


def create_test_file(tests_file_path: str, models_file_path: str, test_data: Dict[str, Dict]) -> None:
    """Create the test file with validation tests for all models."""
    tests_path = Path(tests_file_path)
    ensure_directory_exists(tests_path)
    models_import_path = Path(models_file_path).stem
    valid_test_data = {k: v for k, v in test_data.items() if v}
    if not valid_test_data:
        logger.warning("No valid test data found, creating minimal test file")
        test_content = f'''"""
Auto-generated validation tests for Pydantic models.
Generated on: {time.strftime('%Y-%m-%d %H:%M:%S')}
No valid models found for testing.
"""
import pytest

def test_placeholder():
    """Placeholder test - no valid models found."""
    assert True
'''
    else:
        test_content = f'''"""
Auto-generated validation tests for Pydantic models.
Generated on: {time.strftime('%Y-%m-%d %H:%M:%S')}
"""
import pytest
from typing import Dict, Any
from pydantic import BaseModel, ValidationError
from {models_import_path} import {", ".join(valid_test_data.keys())}


def generic_model_validation_test(model_to_test: BaseModel, example_input: Dict[str, Any]) -> None:
    """
    Generic test function that validates a model with example input.

    Args:
        model_to_test: The Pydantic model class to test
        example_input: Dictionary with example input data
    """
    try:
        # Test successful validation
        validated_model = model_to_test.model_validate(example_input)
        assert validated_model is not None

        # Test that we can convert back to dict
        model_dict = validated_model.model_dump()
        assert isinstance(model_dict, dict)

    except ValidationError as e:
        pytest.fail(f"Validation failed for {{model_to_test.__name__}}: {{e}}")
    except Exception as e:
        pytest.fail(f"Unexpected error for {{model_to_test.__name__}}: {{e}}")


# Individual test functions for each model
'''

        # Generate individual test functions for each model
        for model_name, example_data in valid_test_data.items():
            test_content += f'''
def test_{model_name.lower()}_validation():
    """Test validation for {model_name} model."""
    example_input = {json.dumps(example_data, indent=4)}

    generic_model_validation_test({model_name}, example_input)


def test_{model_name.lower()}_validation_with_invalid_data():
    """Test validation failure for {model_name} model with invalid data."""
    invalid_input = {{"invalid_field": "should_fail"}}

    with pytest.raises(ValidationError):
        {model_name}.model_validate(invalid_input)
'''

        # Add parametrized test for all models
        if valid_test_data:
            test_content += f'''

# Parametrized test for all models
@pytest.mark.parametrize("model_class,example_input", [
'''

            for model_name, example_data in valid_test_data.items():
                test_content += f'    ({model_name}, {json.dumps(example_data)}),\n'

            test_content += '''
])
def test_all_models_validation(model_class: BaseModel, example_input: Dict[str, Any]):
    """Parametrized test for all models."""
    generic_model_validation_test(model_class, example_input)
'''

    # Write the test file
    with open(tests_path, 'w') as f:
        f.write(test_content)

    logger.info(f"Created test file at {tests_file_path}")
