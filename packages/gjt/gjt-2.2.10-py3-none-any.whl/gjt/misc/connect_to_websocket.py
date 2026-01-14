import asyncio
from contextlib import asynccontextmanager
from typing import Optional, Callable, Protocol, Any
from websockets import connect
from gjt.misc.get_network_data import get_network_data
from gjt.misc.get_error_data import get_error_data
import json
from typing import Any, Optional, Tuple
from loguru import logger
class EmpireWebSocket(Protocol):
    async def send(self, message: Any) -> None: ...
    async def recv(self) -> Any: ...
    async def wait_closed(self) -> None: ...
    async def close(self, code: int = 1000, reason: str = "") -> None: ...

KEEPALIVE_INTERVAL = 60
RECONNECT_DELAY = 10

class WSWrapper:
    def __init__(self):
        self.ws: Optional[EmpireWebSocket] = None
        self.server: Optional[str] = None
        self.kingdom: Optional[int] = None
        self.queue: asyncio.Queue[str] = asyncio.Queue()
        # per-tag queues for concurrent receivers
        self._tag_queues: dict[str, asyncio.Queue[str]] = {}
        self._listener: Optional[asyncio.Task] = None

    async def send(self, data: Any):
        assert self.ws is not None
        logger.debug(f"Sending data: {data}")
        try:
            await self.ws.send(data)
            return True
        except Exception as e:
            logger.error(f"Error sending data: {e}", exc_info=True)
            return False

    async def send_json(self, tag: str, payload: Any) -> bool:
        """
        Send JSON message to the server.
        
        :param tag: tag of the message
        :type tag: str
        :param payload: json payload of the message
        :type payload: Any
        :param sync: whether to wait for a response
        :type sync: bool
        """
        assert self.server is not None
        logger.debug(f"Sending JSON message with tag='{tag}', payload={payload}")
        try:
            await self.send(f"%xt%{get_network_data(self.server, "prefix")}%{tag}%1%{json.dumps(payload)}%")
            return True
        except ConnectionError as e:
            logger.error(f"ConnectionError when sending JSON message with tag='{tag}': {e}", exc_info=True)
            return False
        except TimeoutError as e:
            logger.error(f"TimeoutError when sending JSON message with tag='{tag}': {e}", exc_info=True)
            return False
        except Exception as e:
            logger.error(f"Unexpected error when sending JSON message with tag='{tag}': {e}", exc_info=True)
            return False
        
    async def send_rjs(self, tag: str, payload: Any) -> dict | bool | str:
        """
        Send JSON message to the server.
        
        :param tag: tag of the message
        :type tag: str
        :param payload: json payload of the message
        :type payload: Any
        :param sync: whether to wait for a response
        :type sync: bool
        """
        assert self.server is not None
        logger.debug(f"Sending JSON message with tag='{tag}' payload={payload}")
        try:
            await self.send(f"%xt%{get_network_data(self.server, "prefix")}%{tag}%1%{json.dumps(payload)}%")
            return await self.recv(tag)
        except ConnectionError as e:
            logger.error(f"ConnectionError when sending RJS message with tag='{tag}': {e}", exc_info=True)
            return False
        except TimeoutError as e:
            logger.error(f"TimeoutError when sending RJS message with tag='{tag}': {e}", exc_info=True)
            return False
        except Exception as e:
            logger.error(f"Unexpected error when sending RJS message with tag='{tag}': {e}", exc_info=True)
            return False
    
    async def send_xml(self, t: str, action: str, r: str, data: str):
        logger.debug(f"Sending XML message with t='{t}', action='{action}', r='{r}'")
        return await self.send(f"<msg t='{t}'><body action='{action}' r='{r}'>{data}</body></msg>")

    async def recv(self, tag: str, timeout: Optional[float] = None) -> dict | str:
        """
        Returns:
            - Data (dict/str) if error code == 0
            - Error code (str) if error code != 0
        
        Args:
            tag: The message tag to wait for
            timeout: Optional timeout in seconds. If None, waits indefinitely.
        
        Raises:
            asyncio.TimeoutError: If timeout is specified and exceeded
        """
        logger.debug(f"Waiting to receive message with tag='{tag}' (timeout={timeout}s)")
        
        # use a per-tag queue so multiple coroutines can wait on different tags
        q = self._tag_queues.setdefault(tag, asyncio.Queue())

        async def _recv_impl():
            while True:
                raw = await q.get()
                if isinstance(raw, bytes):
                    raw = raw.decode("utf-8", errors="ignore")
                logger.debug(f"Received raw message on tag queue '{tag}': {raw[:100]}..." if len(raw) > 100 else f"Received raw message: {raw}")

                # message expected to be in the %xt% format; parse payload and error
                if not raw.startswith("%xt%"):
                    logger.debug("Message does not start with '%xt%', ignoring")
                    continue

                body = raw[4:]

                try:
                    _, rest = body.split("%", 1)
                except ValueError:
                    logger.debug("Message body does not contain expected '%', ignoring")
                    continue

                if not rest.startswith("1%"):
                    logger.debug("Message does not start with '1%', ignoring")
                    continue

                rest = rest[2:]

                try:
                    err_str, rest = rest.split("%", 1)
                    err = int(err_str)
                except ValueError:
                    logger.debug("Error code is not an integer, ignoring")
                    continue

                # payload should end with % or be empty (after last %)
                if rest.endswith("%"):
                    payload = rest[:-1]
                elif rest == "":
                    payload = ""
                else:
                    logger.debug("Message payload not properly terminated, ignoring")
                    continue

                if err != 0:
                    logger.warning(f"Received error response for tag='{tag}': {err}")
                    return get_error_data(err)

                try:
                    result = json.loads(payload)
                    logger.debug(f"Successfully parsed JSON response for tag='{tag}'")
                    return result
                except json.JSONDecodeError:
                    logger.debug(f"Response for tag='{tag}' is not JSON, returning as string")
                    return payload
        
        if timeout is None:
            return await _recv_impl()
        else:
            try:
                return await asyncio.wait_for(_recv_impl(), timeout=timeout)
            except asyncio.TimeoutError:
                logger.error(f"Timeout waiting for message with tag='{tag}' after {timeout}s")
                raise asyncio.TimeoutError()

    async def recv_any(self, tags: list[str], timeout: Optional[float] = None) -> Tuple[str, dict | str]:
        """Wait for any of the provided tags and return a tuple (tag, payload).

        This will not consume messages for other tags.
        """
        logger.debug(f"Waiting for any of tags={tags} (timeout={timeout}s)")

        # ensure queues exist
        queues = [self._tag_queues.setdefault(t, asyncio.Queue()) for t in tags]

        tasks: dict[asyncio.Task, str] = {}
        for tag, q in zip(tags, queues):
            tasks[asyncio.create_task(q.get())] = tag

        try:
            done, pending = await asyncio.wait(tasks.keys(), timeout=timeout, return_when=asyncio.FIRST_COMPLETED)
            if not done:
                logger.error(f"Timeout waiting for any of tags={tags} after {timeout}s")
                raise asyncio.TimeoutError()

            task = next(iter(done))
            tag = tasks[task]
            raw = task.result()
            if isinstance(raw, bytes):
                raw = raw.decode("utf-8", errors="ignore")

            # parse payload similarly to recv
            if not raw.startswith("%xt%"):
                logger.debug("Message does not start with '%xt%', ignoring")
                return tag, raw

            body = raw[4:]
            try:
                _, rest = body.split("%", 1)
            except ValueError:
                logger.debug("Message body does not contain expected '%', returning raw")
                return tag, raw

            if not rest.startswith("1%"):
                logger.debug("Message does not start with '1%', returning raw")
                return tag, raw

            rest = rest[2:]
            try:
                err_str, rest = rest.split("%", 1)
                err = int(err_str)
            except ValueError:
                logger.debug("Error code not integer, returning raw")
                return tag, raw

            # payload should end with % or be empty (after last %)
            if rest.endswith("%"):
                payload = rest[:-1]
            elif rest == "":
                payload = ""
            else:
                logger.debug("Message payload not properly terminated, returning raw")
                return tag, raw

            if err != 0:
                logger.warning(f"Received error response for tag='{tag}': {err}")
                return tag, get_error_data(err)

            try:
                result = json.loads(payload)
                return tag, result
            except json.JSONDecodeError:
                return tag, payload
        finally:
            for t in pending:
                t.cancel()

    def start_listener(self):
        if self._listener:
            self._listener.cancel()
        self._listener = asyncio.create_task(self._listen())

    async def stop_listener(self):
        if self._listener:
            self._listener.cancel()
            try:
                await self._listener
            except asyncio.CancelledError:
                pass
            self._listener = None

    async def _listen(self):
        assert self.ws is not None
        logger.debug("Starting WebSocket listener")
        try:
            while True:
                msg = await self.ws.recv()
                # keep the raw queue for compatibility
                await self.queue.put(msg)

                # also dispatch to a per-tag queue if we can extract a tag
                try:
                    raw = msg
                    if isinstance(raw, bytes):
                        raw = raw.decode("utf-8", errors="ignore")

                    if raw.startswith("%xt%"):
                        body = raw[4:]
                        short, _ = body.split("%", 1)
                        tag_q = self._tag_queues.setdefault(short, asyncio.Queue())
                        await tag_q.put(msg)
                except Exception:
                    logger.debug("Failed to dispatch incoming message to tag queue", exc_info=True)
        except Exception as e:
            logger.error(f"Error in WebSocket listener: {e}", exc_info=True)

async def _keepalive_task(server: str, wrapper: WSWrapper, alive: Callable[[], bool]):
    logger.debug(f"Starting keepalive task for server '{server}'")
    try:
        while alive():
            await asyncio.sleep(KEEPALIVE_INTERVAL)
            if wrapper.ws:
                logger.debug("Sending keepalive ping")
                await wrapper.send(f"%xt%{get_network_data(server, "prefix")}%pin%1%<RoundHouseKick>%")
    except asyncio.CancelledError:
        logger.debug("Keepalive task cancelled")


@asynccontextmanager
async def connect_to_websocket(server: str, **kwargs):
    logger.info(f"Connecting to WebSocket server '{server}'")
    wrapper = WSWrapper()
    alive = True

    async def manage():
        nonlocal alive
        keepalive: Optional[asyncio.Task] = None

        while alive:
            try:
                logger.info(f"Attempting to connect to WebSocket server '{server}'")
                wrapper.ws = await connect(get_network_data(server, "wss"), **kwargs)
                logger.info(f"Connected to WebSocket server '{server}'")
                await wrapper.send_xml("sys", "verChk","0", "<ver v='166'/>")
                await wrapper.send_xml("sys", "login","0", f"<login z='{get_network_data(server, "prefix")}'><nick><![CDATA[]]></nick><pword><![CDATA[1136017%pl%0]]></pword></login>")
                await wrapper.send_xml("sys", "autoJoin", "-1", "")
                await wrapper.send_xml("sys", "roundTrip", "1", "")
                wrapper.server = server
                logger.debug("Starting listener task")
                wrapper.start_listener()
                keepalive = asyncio.create_task(
                    _keepalive_task(server, wrapper, lambda: alive)
                )

                assert wrapper.ws is not None
                logger.debug("Waiting for WebSocket to close")
                await wrapper.ws.wait_closed()
                logger.info(f"WebSocket connection to '{server}' closed")

            except Exception as e:
                logger.error(f"Error in WebSocket connection loop: {e}", exc_info=True)
            finally:
                if keepalive:
                    keepalive.cancel()
                    try:
                        await keepalive
                    except asyncio.CancelledError:
                        pass
                    keepalive = None

                await wrapper.stop_listener()

            if not alive:
                logger.debug("WebSocket alive flag is False, breaking connection loop")
                break

            logger.info(f"Reconnecting to WebSocket server '{server}' in {RECONNECT_DELAY} seconds...")
            await asyncio.sleep(RECONNECT_DELAY)

    manager_task = asyncio.create_task(manage())

    while wrapper.ws is None:
        await asyncio.sleep(0.05)

    try:
        logger.debug(f"WebSocket context manager initialized for server '{server}'")
        yield wrapper
    finally:
        logger.info(f"Closing WebSocket connection to '{server}'")
        alive = False
        manager_task.cancel()
        try:
            await manager_task
        except asyncio.CancelledError:
            logger.debug("Manager task cancelled")
            pass

        if wrapper.ws:
            try:
                logger.debug(f"Closing WebSocket connection")
                await wrapper.ws.close()
            except Exception as e:
                logger.warning(f"Error closing WebSocket: {e}")

        await wrapper.stop_listener()
        logger.info(f"WebSocket connection to '{server}' fully closed")
