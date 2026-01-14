from ..misc.connect_to_websocket import WSWrapper
from loguru import logger

async def build_building(ws: WSWrapper, building_id: int, x: int, y: int, rotated: int = 0, sync: bool = False) -> bool | dict:
    """
    Docstring for build_building
    
    :param ws: Description
    :type ws: WSWrapper
    :param building_id: Description
    :type building_id: int
    :param x: Description
    :type x: int
    :param y: Description
    :type y: int
    :param rotated: Description
    :type rotated: int
    """
    build_data = {
        "WID":building_id,
        "X":x,
        "Y":y,
        "R":rotated,
        "PWR":0,
        "PO":-1,
        "DOID":-1
        }
    try:
        await ws.send_json("ebu", build_data)
        if sync:
            data = await ws.recv("ebu", timeout=12)
            if isinstance(data, dict):
                return data["O"][1]
            else:
                logger.error(f"Error in build_building: {data}")
                return False
        else:
            return True
    except ConnectionError as e:
        logger.error(f"ConnectionError when building: {e}", exc_info=True)
        return False
    except TimeoutError as e:
        logger.error(f"TimeoutError when building: {e}", exc_info=True)
        return False
    except Exception as e:
        logger.error(f"Unexpected error when building: {e}", exc_info=True)
        return False
    
async def free_skip_building(ws: WSWrapper, building_id: int, free_skip: int = 1) -> bool:
    skip_data = {
        "OID": building_id,
        "FS": free_skip
        }
    try:
        await ws.send_json("fco", skip_data)
        return True
    except ConnectionError as e:
        logger.error(f"ConnectionError when skipping build: {e}", exc_info=True)
        return False
    except TimeoutError as e:
        logger.error(f"TimeoutError when skipping build: {e}", exc_info=True)
        return False
    except Exception as e:
        logger.error(f"Unexpected error when skipping build: {e}", exc_info=True)
        return False