class MappingNotFoundException(Exception):
    pass

class StepInitializationError(Exception):
    pass

class FileParsingError(Exception):
    """Raised when file parsing fails."""
    pass

class MapperLoadError(Exception):
    """Raised when loading the RITA mapper fails."""
    pass

class ConfigNotFoundError(Exception):
    """Raised when a configuration is not found."""
    pass

class ConfigValidationError(Exception):
    """Raised when configuration validation fails."""
    pass

class StepConfigValidationError(Exception):
    """Raised when a step configuration validation fails."""
    pass