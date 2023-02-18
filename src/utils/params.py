from lpastarProcess.pf_exceptions import MapInitializationException
from typing import Dict, Any

paramlpastar={
            "width": 3000,
            "height": 2000,
            "resolution": 50,
            "free_case_value": 1,
            "obstacle_case_value": 1000,
            "heuristics_multiplier": 1,
            "period" : 2,
            "timeout" : 10
            }

paramlidar={
            "dmin" : 50,
            "group": 3 
            }


def __param_getter(self, param_name: str, params: Dict[str, Any]) -> Any:
    """ A function which is used to extract data
        from dictionary and verify that all required
        arguments have been provided.

        Args:
            param_name (str):
                A name of an argument to extract
            params (Dict[str, Any]):
                A dictionary to extract from

        Raises:
            MapInitializationException: Occurs when the
            required argument is missing

        Returns:
            Any: A value extracted from **params**
            associated to the key **param_name**
        """
    print(param_name, params)
    if param_name in params.keys():
        return params[param_name]
    raise MapInitializationException("Parameter required, \
                    but not provided: " + param_name)
