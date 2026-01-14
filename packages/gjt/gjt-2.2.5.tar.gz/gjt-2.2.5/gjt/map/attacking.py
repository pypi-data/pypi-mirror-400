from ..misc.connect_to_websocket import WSWrapper
import json
from loguru import logger
from typing import cast
from gjt.map.switch_kingdoms import get_kingdom_data


async def pre_attacking(ws: WSWrapper, target_kingdom: int | None = None, coords: list = []) -> dict | str:
    """
    Docstring for pre_attacking
    
    :param ws: Description
    :type ws: WSWrapper
    :param target_kingdom: Description
    :type target_kingdom: int | None
    """
    wrapper = ws
    if target_kingdom is None: raise ValueError("Target kingdom cannot be None")

    json_data = {
        "CD": 1
        }

    try:
        data = {
            "SX":coords[0],
            "SY":coords[1],
            "TX":coords[2],
            "TY":coords[3],
            "KID":target_kingdom
        }
        response = await ws.send_rjs("adi", data)
        assert isinstance(response, dict | str), f"Expected dict or str response, got: {type(response)}"
        return response
    except ConnectionError as e:
        logger.error(f"ConnectionError when fetching castle data: {e}", exc_info=True)
        return {"error": "ConnectionError"}
    except TimeoutError as e:
        logger.error(f"TimeoutError when fetching castle data: {e}", exc_info=True)
        return {"error": "TimeoutError"}
    except Exception as e:
        logger.error(f"Unexpected error when fetching castle data: {e}", exc_info=True)
        return {"error": "UnexpectedError"}

async def attacking(ws: WSWrapper, scoords: list, tcoords: list, target_kingdom: str, waves: dict) -> None:
    """
    Docstring for attacking
    
    :param waves: Description
    :type waves: dict
    """
    data = {
    "SX":726,
    "SY":939,
    "TX":732,
    "TY":941,
    "KID":0,
    "LID":0,
    "WT":0,
    "HBW":-1,
    "BPC":0,
    "ATT":0,
    "AV":0,
    "LP":0,
    "FC":0,
    "PTT":1,
    "SD":0,
    "ICA":0,
    "CD":99,
    "A":[waves],
    "ASCT":0
    }