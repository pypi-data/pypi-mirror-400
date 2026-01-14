from gjt.misc.connect_to_websocket import WSWrapper
import asyncio, random
from loguru import logger

async def login_to_account(ws: WSWrapper, username: str, password: str) -> bool:
    if ws is None: raise ValueError("Login error: ws cannot be None")
    wrapper = ws
    try:
        logger.info(f"Logging in to account '{username}'")
        login_data = {
            "CONM":696,
            "RTM":54,
            "ID":0,
            "PL":1,
            "NOM":username,
            "PW":password,
            "LT":None,
            "LANG":"pl",
            "DID":"0",
            "AID":"1748087142659830366",
            "KID":"",
            "REF":"https://empire.goodgamestudios.com",
            "GCI":"",
            "SID":9,
            "PLFID":1
            }
        await wrapper.send_json("vln", f'{{"NOM": {username}}}')
        await asyncio.sleep(random.uniform(0.5, 1.5))
        login_message = await wrapper.send_rjs("lli", login_data)
        if login_message:
            if "LOGIN_COOLDOWN" in str(login_message) or "INVALID_PASSWORD" in str(login_message):
                logger.error(f"Login failed for account '{username}': {login_message}")
                return False
            logger.debug("Got login resp" + str(login_message))
        await wrapper.send_json("nch", None)
        await wrapper.send_json("core_gic", {"T":"link","CC":"PL","RR":"html5"})
        await wrapper.send_json("gbl", '{}')
        await wrapper.send_json("jca", '{"CID":-1,"KID":0}')
        await wrapper.send_json("alb", '{}')
        await wrapper.send_json("sli", '{}')
        await wrapper.send_json("gie", '{}')
        await wrapper.send_json("asc", '{}')
        await wrapper.send_json("sie", '{}')
        await wrapper.send_json("kli", '{}')
        data = await wrapper.send_rjs("ffi", '{"FIDS":[1]}')
        await wrapper.send_json("kli", '{}')
        if data:
            await wrapper.send_json("gcs", '{}')
        logger.info(f"Logged in to account '{username}' successfully")
        return True
    except ConnectionError as e:
        logger.error(f"ConnectionError when logging in: {e}", exc_info=True)
        return False
    except TimeoutError as e:
        logger.error(f"TimeoutError when logging in: {e}", exc_info=True)
        return False
    except Exception as e:
        logger.error(f"Unexpected error when logging in: {e}", exc_info=True)
        return False