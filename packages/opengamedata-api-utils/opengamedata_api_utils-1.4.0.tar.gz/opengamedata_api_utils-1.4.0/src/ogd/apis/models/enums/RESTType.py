from enum import IntEnum
from typing import Set

class RESTType(IntEnum):
    """Simple enumerated type to track type of a REST request.
    """
    GET  = 1
    POST = 2
    PUT  = 3

    def __str__(self):
        """Stringify function for RESTTypes.

        :return: Simple string version of the name of a RESTType
        :rtype: _type_
        """
        match self.value:
            case RESTType.GET:
                return "GET"
            case RESTType.POST:
                return "POST"
            case RESTType.PUT:
                return "PUT"
            case _:
                return "INVALID REST TYPE"