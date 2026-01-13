from typing import Any, Callable, Dict, Union

Random = object()
Default = object()


class DefaultValue:
    """
    A wrapper class to hold a default value.

    This class allows for lazy evaluation of default values if a callable is provided.
    """

    def __init__(self, value: Union[Any, Callable[[], Any]]):
        """
        Initializes the DefaultValue with a given value or a callable that returns a value.

        :param value: The default value or a callable that returns the default value.
        """
        self._value = value

    @property
    def value(self) -> Any:
        if callable(self._value):
            return self._value()
        return self._value


def clean_passed_parameters(parameters: Dict[str, Any]) -> Dict[str, Any]:
    """
    Cleans a dictionary of parameters by removing entries that are None, Default, or Random.

    This function is used to filter out arguments that were not explicitly provided by the user
    (i.e., they have their default sentinel values) so that the random parameter generation logic
    can take over for those missing values.

    Args:
        parameters (Dict[str, Any]): A dictionary of parameters to clean.

    Returns:
        Dict[str, Any]: A new dictionary containing only the parameters that have explicit values
                        (i.e., not None, Default, or Random).
    """
    return {
        k: v for k, v in parameters.items()
        if v is not None and v is not Default and v is not Random
    }
