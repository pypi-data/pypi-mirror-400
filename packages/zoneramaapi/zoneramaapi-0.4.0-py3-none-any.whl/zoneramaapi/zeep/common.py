from zeep.proxy import ServiceProxy, AsyncServiceProxy
from zoneramaapi.errors import ZoneramaError


def raise_for_error(response, action: str) -> None:
    if not response.Success:
        if response.Code == "E_ZONERAMA_NEEDLOGIN":
            raise ZoneramaError(f"Cannot {action} because the client is not logged in.")
        raise ZoneramaError(f"Failed to {action}.", response.Message, response.Code)
