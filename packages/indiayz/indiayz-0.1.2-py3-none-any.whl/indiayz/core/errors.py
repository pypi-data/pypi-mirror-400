class IndiayzError(Exception):
    """Base exception for indiayz."""
    pass


class ModuleNotAvailable(IndiayzError):
    pass


class ConfigurationError(IndiayzError):
    pass
