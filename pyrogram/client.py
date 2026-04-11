#  Pyrogram - Telegram MTProto API Client Library for Python
#  Copyright (C) 2017-present Dan <https://github.com/delivrance>
#
#  This file is part of Pyrogram.
#
#  Pyrogram is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Lesser General Public License as published
#  by the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  Pyrogram is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Lesser General Public License for more details.
#
#  You should have received a copy of the GNU Lesser General Public License
#  along with Pyrogram.  If not, see <http://www.gnu.org/licenses/>.

import asyncio
import logging
import os
import platform
import random
import re
import shutil
import sys
import time
from collections import OrderedDict
from concurrent.futures.thread import ThreadPoolExecutor
from contextlib import suppress
from datetime import datetime
from hashlib import sha256
from importlib import import_module
from io import BytesIO, StringIO
from mimetypes import MimeTypes
from pathlib import Path
from typing import AsyncGenerator, Callable, List, Optional, Type, Union

import pyrogram
from pyrogram import __license__, __version__, enums, raw, utils
from pyrogram.crypto import aes
from pyrogram.errors import (
    AuthBytesInvalid,
    BadRequest,
    CDNFileHashMismatch,
    ChannelPrivate,
    FloodPremiumWaitX,
    FloodWaitX,
    PersistentTimestampInvalid,
    PersistentTimestampOutdated,
    SessionPasswordNeeded,
    Unauthorized,
    FileTokenInvalid,
    RequestTokenInvalid,
    AuthTokenExpired
)
from pyrogram.handlers.handler import Handler
from pyrogram.methods import Methods
from pyrogram.qrlogin import QRLogin
from pyrogram.session import Auth, Session
from pyrogram.storage import SQLiteStorage, Storage
from pyrogram.types import LinkPreviewOptions, TermsOfService, User
from pyrogram.utils import ainput, invoke_callable

from .connection import Connection
from .connection.transport import TCP, TCPAbridged
from .connection.endpoint_selector import select_best_dc_option
from .dispatcher import Dispatcher
from .file_id import FileId, FileType, ThumbnailSource
from .mime_types import mime_types
from .parser import Parser
from .session.internals import MsgId

log = logging.getLogger(__name__)

# Built-in Telegram API keys from official clients.
# Some may be expired; if authorization fails, re-run to try another one.
BUILTIN_API_KEYS = [
    (4, "014b35b6184100b085b0d0572f9b5103"),        # Telegram Android
    (6, "eb06d4abfb49dc3eeb1aeb98ae0f581e"),        # Telegram Android
    (8, "7245de8e747a0d6fbe11f7cc14fcc0bb"),        # Telegram iOS
    (10840, "33c45224029d59cb3ad0c16134215aeb"),     # Telegram iOS
    (2834, "68875f756c9b437a8b916ca3de215815"),      # Telegram MacOS
    (611335, "d524b414d21f4d37f08684c1df41ac9c"),    # Telegram Desktop
    (2040, "b18441a1ff607e10a989891a5462e627"),      # Telegram Desktop
    (2521, "64d20abd7ee359213579e9a599fde866"),      # Telegram Android S
    (5, "1c5c96d5edd401b1ed40db3fb5633e2d"),         # Telegram Android S
    (21724, "3e0cb5efcd52300aec5994fdfc5bdc16"),     # Telegram Android X
    (94575, "a3406de8d171bb422bb6ddf3bbd800e2"),     # Telegram Database Library
    (1025907, "452b0359b988148995f22ff0f4229750"),   # Telegram Web K
    (2496, "8da85b0d5bfe62527e5b244c209159c3"),      # Telegram Web Z
]


class Client(Methods):
    """Pyrogram Client, the main means for interacting with Telegram.

    Parameters:
        name (``str``):
            A name for the client, e.g.: "my_account".

        api_id (``int`` | ``str``, *optional*):
            The *api_id* part of the Telegram API key, as integer or string.
            E.g.: 12345 or "12345".

        api_hash (``str``, *optional*):
            The *api_hash* part of the Telegram API key, as string.
            E.g.: "0123456789abcdef0123456789abcdef".

        app_version (``str``, *optional*):
            Application version.
            Defaults to "Pyrogram x.y.z".

        device_model (``str``, *optional*):
            Device model.
            Defaults to *platform.python_implementation() + " " + platform.python_version()*.

        system_version (``str``, *optional*):
            Operating System version.
            Defaults to *platform.system() + " " + platform.release()*.

        lang_pack (``str``, *optional*):
            Name of the language pack used on the client.
            Defaults to "" (empty string).

        lang_code (``str``, *optional*):
            Code of the language used on the client, in ISO 639-1 standard.
            Defaults to "en".

        system_lang_code (``str``, *optional*):
            Code of the language used on the system, in ISO 639-1 standard.
            Defaults to "en".

        ipv6 (``bool``, *optional*):
            Pass True to connect to Telegram using IPv6.
            If the session was previously used with IPv4,
            the first request will be made via IPv4,
            after which the server address will be updated (works both ways).
            Defaults to False (IPv4).

        proxy (``dict`` | ``str``, *optional*):
            The Proxy settings as dict.
            E.g.: *dict(scheme="socks5", hostname="11.22.33.44", port=1234, username="user", password="pass")*
            or *"http://11.22.33.44:1234"* or *"socks5://user:pass@11.22.33.44:1234"* or *"tg://user:pass@11.22.33.44:1234"*.
            The *username* and *password* can be omitted if the proxy doesn't require authorization.

        test_mode (``bool``, *optional*):
            Enable or disable login to the test servers.
            Only applicable for new sessions and will be ignored in case previously created sessions are loaded.
            Defaults to False.

        bot_token (``str``, *optional*):
            Pass the Bot API token to create a bot session, e.g.: "123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11"
            Only applicable for new sessions.

        session_string (``str``, *optional*):
            Pass a session string to load the session in-memory.
            Implies ``in_memory=True``.

        in_memory (``bool``, *optional*):
            Pass True to start an in-memory session that will be discarded as soon as the client stops.
            In order to reconnect again using an in-memory session without having to login again, you can use
            :meth:`~pyrogram.Client.export_session_string` before stopping the client to get a session string you can
            pass to the ``session_string`` parameter.
            Defaults to False.

        phone_number (``str``, *optional*):
            Pass the phone number as string (with the Country Code prefix included) to avoid entering it manually.
            Only applicable for new sessions.

        phone_code (``str``, *optional*):
            Pass the phone code as string (for test numbers only) to avoid entering it manually.
            Only applicable for new sessions.

        password (``str``, *optional*):
            Pass the Two-Step Verification password as string (if required) to avoid entering it manually.
            Only applicable for new sessions.

        workers (``int``, *optional*):
            Number of maximum concurrent workers for handling incoming updates.
            Defaults to ``min(32, os.cpu_count() + 4)``.

        workdir (``str``, *optional*):
            Define a custom working directory.
            The working directory is the location in the filesystem where Pyrogram will store the session files.
            Defaults to the parent directory of the main script.

        plugins (``dict``, *optional*):
            Smart Plugins settings as dict, e.g.: *dict(root="plugins")*.
            The ``root`` key can be a single string or a list of strings to load plugins from multiple directories,
            e.g.: *dict(root=["plugins", "extra_plugins"])*.

        parse_mode (:obj:`~pyrogram.enums.ParseMode`, *optional*):
            Set the global parse mode of the client. By default, texts are parsed using both Markdown and HTML styles.
            You can combine both syntaxes together.

        no_updates (``bool``, *optional*):
            Pass True to disable incoming updates.
            When updates are disabled the client can't receive messages or other updates.
            Useful for batch programs that don't need to deal with updates.
            Defaults to False (updates enabled and received).

        skip_updates (``bool``, *optional*):
            Pass True to skip pending updates that arrived while the client was offline.
            Doesn't work if *in_memory* is set to True.
            Defaults to True.

        takeout (``bool``, *optional*):
            Pass True to let the client use a takeout session instead of a normal one, implies *no_updates=True*.
            Useful for exporting Telegram data. Methods invoked inside a takeout session (such as get_chat_history,
            download_media, ...) are less prone to throw FloodWait exceptions.
            Only available for users, bots will ignore this parameter.
            Defaults to False (normal session).

        sleep_threshold (``int``, *optional*):
            Set a sleep threshold for flood wait exceptions happening globally in this client instance, below which any
            request that raises a flood wait will be automatically invoked again after sleeping for the required amount
            of time. Flood wait exceptions requiring higher waiting times will be raised.
            Defaults to 10 seconds.

        hide_password (``bool``, *optional*):
            Pass True to hide the password when typing it during the login.
            Defaults to False, because ``getpass`` (the library used) is known to be problematic in some
            terminal environments.

        max_concurrent_transmissions (``int``, *optional*):
            Set the maximum amount of concurrent transmissions (uploads & downloads).
            A value that is too high may result in network related issues.
            Defaults to 1.

        max_message_cache_size (``int``, *optional*):
            Set the maximum size of the message cache.
            Defaults to 1000.

        max_topic_cache_size (``int``, *optional*):
            Set the maximum size of the topic cache.
            Defaults to 1000.

        storage_engine (:obj:`~pyrogram.storage.Storage`, *optional*):
            Pass an instance of your own implementation of session storage engine.
            Useful when you want to store your session in databases like Mongo, Redis, etc.

        client_platform (:obj:`~pyrogram.enums.ClientPlatform`, *optional*):
            The platform where this client is running.
            Defaults to 'other'

        link_preview_options (:obj:`~pyrogram.types.LinkPreviewOptions`, *optional*):
            Global link preview options for the client.

        fetch_replies (``bool``, *optional*):
            Pass True to automatically fetch replies for messages.
            Defaults to True.

        fetch_topics (``bool``, *optional*):
            Pass True to automatically fetch forum topics.
            Defaults to True.

        fetch_stories (``bool``, *optional*):
            Pass True to automatically fetch stories if they are missing.
            Defaults to True.

        fetch_stickers (``bool``, *optional*):
            Pass True to automatically fetch names of sticker sets.
            Defaults to True.

        loop (:py:class:`asyncio.AbstractEventLoop`, *optional*):
            Event loop.

        init_connection_params (``dict``, *optional*):
            Additional initConnection parameters.
            For now, only the tz_offset field is supported, for specifying timezone offset in seconds.
    """

    APP_VERSION = f"Pyrogram {__version__}"
    DEVICE_MODEL = f"{platform.python_implementation()} {platform.python_version()}"
    SYSTEM_VERSION = f"{platform.system()} {platform.release()}"

    LANG_PACK = ""
    LANG_CODE = "en"
    SYSTEM_LANG_CODE = "en"

    PARENT_DIR = Path(sys.argv[0]).parent

    INVITE_LINK_RE = re.compile(r"^(?:https?://)?(?:www\.)?(?:t(?:elegram)?\.(?:org|me|dog)/(?:joinchat/|\+))([\w-]+)$")
    UPGRADED_GIFT_RE = re.compile(r"^(?:https?://)?(?:www\.)?(?:t(?:elegram)?\.(?:org|me|dog)/(?:nft/|\+))([\w-]+)$")
    SAVED_GIFT_RE = re.compile(r"^(-\d+)_(\d+)$")
    CHANNEL_MESSAGE_LINK_RE = re.compile(r"^(?:https?://)?(?:www\.)?(?:t(?:elegram)?\.(?:org|me|dog)/(?:c/)?)([\w]+)(?:.+)?$")
    WORKERS = min(32, (os.cpu_count() or 0) + 4)  # os.cpu_count() can be None
    WORKDIR = PARENT_DIR

    # Interval of seconds in which the updates watchdog will kick in
    UPDATES_WATCHDOG_INTERVAL = 5 * 60

    MAX_CONCURRENT_TRANSMISSIONS = 3
    MAX_MESSAGE_CACHE_SIZE = 1000
    MAX_TOPIC_CACHE_SIZE = 1000

    mimetypes = MimeTypes()
    mimetypes.readfp(StringIO(mime_types))

    def __init__(
        self,
        name: str,
        api_id: Optional[Union[int, str]] = None,
        api_hash: Optional[str] = None,
        app_version: str = APP_VERSION,
        device_model: str = DEVICE_MODEL,
        system_version: str = SYSTEM_VERSION,
        lang_pack: str = LANG_PACK,
        lang_code: str = LANG_CODE,
        system_lang_code: str = SYSTEM_LANG_CODE,
        ipv6: Optional[bool] = False,
        proxy: Optional[Union[dict, str]] = None,
        test_mode: Optional[bool] = False,
        bot_token: Optional[str] = None,
        session_string: Optional[str] = None,
        in_memory: Optional[bool] = None,
        phone_number: Optional[str] = None,
        phone_code: Optional[str] = None,
        password: Optional[str] = None,
        workers: int = WORKERS,
        workdir: Union[str, Path] = WORKDIR,
        plugins: Optional[dict] = None,
        parse_mode: "enums.ParseMode" = enums.ParseMode.DEFAULT,
        no_updates: Optional[bool] = None,
        skip_updates: Optional[bool] = True,
        takeout: Optional[bool] = None,
        sleep_threshold: int = Session.SLEEP_THRESHOLD,
        hide_password: Optional[bool] = False,
        max_concurrent_transmissions: int = MAX_CONCURRENT_TRANSMISSIONS,
        max_message_cache_size: int = MAX_MESSAGE_CACHE_SIZE,
        max_topic_cache_size: int = MAX_TOPIC_CACHE_SIZE,
        storage_engine: Optional[Storage] = None,
        client_platform: "enums.ClientPlatform" = enums.ClientPlatform.OTHER,
        link_preview_options: Optional[LinkPreviewOptions] = None,
        fetch_replies: Optional[bool] = True,
        fetch_topics: Optional[bool] = True,
        fetch_stories: Optional[bool] = True,
        fetch_stickers: Optional[bool] = True,
        init_connection_params: Optional[dict] = None,
        connection_factory: Type[Connection] = Connection,
        protocol_factory: type = TCPAbridged,
        loop: Optional[asyncio.AbstractEventLoop] = None
    ):
        super().__init__()

        self.name = name
        if api_id is not None:
            try:
                self.api_id = int(api_id)
            except (ValueError, TypeError) as e:
                raise ValueError(f"api_id must be numeric, got {api_id!r}") from e
        else:
            self.api_id = None

        if self.api_id is None or api_hash is None:
            chosen = random.choice(BUILTIN_API_KEYS)
            if self.api_id is None:
                self.api_id = chosen[0]
            if api_hash is None:
                api_hash = chosen[1]
            log.info(
                "No API key provided, using built-in api_id=%s. "
                "If authorization fails, the key may be expired — please re-run to try another one.",
                self.api_id
            )

        self.api_hash = api_hash
        self.app_version = app_version
        self.device_model = device_model
        self.system_version = system_version
        self.lang_pack = lang_pack.lower()
        self.lang_code = lang_code.lower()
        self.system_lang_code = system_lang_code.lower()
        self.ipv6 = ipv6
        self.proxy = proxy
        self.test_mode = test_mode
        self.bot_token = bot_token
        self.session_string = session_string
        self.in_memory = in_memory
        self.phone_number = phone_number
        self.phone_code = phone_code
        self.password = password
        self.workers = workers
        self.workdir = Path(workdir)
        self.plugins = plugins
        self.parse_mode = parse_mode
        self.no_updates = no_updates
        self.skip_updates = skip_updates
        self.takeout = takeout
        self.sleep_threshold = sleep_threshold
        self.hide_password = hide_password
        self.max_concurrent_transmissions = max_concurrent_transmissions
        self.max_message_cache_size = max_message_cache_size
        self.max_topic_cache_size = max_topic_cache_size
        self.client_platform = client_platform
        self.link_preview_options = link_preview_options
        self.fetch_replies = fetch_replies
        self.fetch_topics = fetch_topics
        self.fetch_stories = fetch_stories
        self.fetch_stickers = fetch_stickers
        self.init_connection_params = init_connection_params
        self.connection_factory = connection_factory
        self.protocol_factory = protocol_factory

        if self.workers < 1:
            raise ValueError(f"workers must be >= 1, got {self.workers}")
        if self.max_concurrent_transmissions < 1:
            raise ValueError(f"max_concurrent_transmissions must be >= 1, got {self.max_concurrent_transmissions}")

        self.executor = ThreadPoolExecutor(self.workers, thread_name_prefix="Handler")

        self.storage: Storage

        if self.session_string:
            self.storage = SQLiteStorage(
                self.name,
                workdir=self.workdir,
                session_string=self.session_string,
                in_memory=True
            )
        elif self.in_memory:
            self.storage = SQLiteStorage(self.name, workdir=self.workdir, in_memory=True)
        elif storage_engine is not None:
            if not isinstance(storage_engine, Storage):
                raise TypeError(
                    f"storage_engine must be a Storage instance, got {type(storage_engine).__name__}"
                )
            self.storage = storage_engine
        else:
            self.storage = SQLiteStorage(self.name, workdir=self.workdir)

        self.dispatcher: Dispatcher = Dispatcher(self)

        self.rnd_id = MsgId
        self._server_time_offset = 0.0

        self.parser: Parser = Parser(self)

        self.session: Optional[Session] = None

        self.business_connections = Cache(500)

        self.sessions = {}
        self.media_sessions = {}
        self.sessions_lock = asyncio.Lock()
        self._session_futures = {}

        self.save_file_semaphore = asyncio.Semaphore(self.max_concurrent_transmissions)
        self.get_file_semaphore = asyncio.Semaphore(self.max_concurrent_transmissions)

        self.is_connected = None
        self.is_initialized = None

        self.takeout_id = None

        self.start_handler = None
        self.stop_handler = None
        self.connect_handler = None
        self.disconnect_handler = None

        self.me: Optional[User] = None

        self.message_cache = Cache(self.max_message_cache_size)
        self.topic_cache = Cache(self.max_topic_cache_size)

        # Sometimes, for some reason, the server will stop sending updates and will only respond to pings.
        # This watchdog will invoke updates.GetState in order to wake up the server and enable it sending updates again
        # after some idle time has been detected.
        self.updates_watchdog_task = None
        self.updates_watchdog_event = asyncio.Event()
        self.last_update_time = datetime.now()
        self._last_update_monotonic = time.monotonic()

        self.listeners = {listener_type: [] for listener_type in pyrogram.enums.ListenerTypes}

        if isinstance(loop, asyncio.AbstractEventLoop):
            self.loop = loop
        else:
            self.loop = None

        self.__config: Optional["raw.types.Config"] = None

    @property
    def loop(self) -> asyncio.AbstractEventLoop:
        if not self._loop:
            self._loop = utils.get_event_loop()
        return self._loop

    @loop.setter
    def loop(self, value: asyncio.AbstractEventLoop):
        self._loop = value

    def __enter__(self):
        return utils.get_event_loop().run_until_complete(self.start())

    def __exit__(self, *args):
        try:
            utils.get_event_loop().run_until_complete(self.stop())
        except ConnectionError:
            pass

    async def __aenter__(self):
        return await self.start()

    async def __aexit__(self, *args):
        try:
            await self.stop()
        except ConnectionError:
            pass

    async def updates_watchdog(self):
        while True:
            try:
                await asyncio.wait_for(self.updates_watchdog_event.wait(), self.UPDATES_WATCHDOG_INTERVAL)
            except asyncio.TimeoutError:
                pass
            else:
                break

            if time.monotonic() - self._last_update_monotonic > self.UPDATES_WATCHDOG_INTERVAL:
                try:
                    await self.invoke(raw.functions.updates.GetState())
                    await self.recover_gaps()
                except Exception as e:
                    log.warning("updates_watchdog invoke failed: %s - %s", type(e).__name__, e)

    async def authorize(self) -> User:
        if self.bot_token:
            return await self.sign_in_bot(self.bot_token)

        print(f"Welcome to Pyrogram (version {__version__})")
        print(f"Pyrogram is free software and comes with ABSOLUTELY NO WARRANTY. Licensed\n"
              f"under the terms of the {__license__}.\n")

        while True:
            try:
                if not self.phone_number:
                    while True:
                        value = await ainput("Enter phone number or bot token: ", loop=self.loop)

                        if not value:
                            continue

                        confirm = await ainput(f'Is "{value}" correct? (y/N): ', loop=self.loop)

                        if confirm.lower() == "y":
                            break

                    if ":" in value:
                        self.bot_token = value
                        return await self.sign_in_bot(value)
                    else:
                        self.phone_number = value

                sent_code = await self.send_phone_number_code(self.phone_number)
            except BadRequest as e:
                print(e.MESSAGE)
                self.phone_number = None
                self.bot_token = None
            else:
                break

        if sent_code.type == enums.SentCodeType.SETUP_EMAIL_REQUIRED:
            print("Setup email required for authorization")

            while True:
                try:
                    while True:
                        email = await ainput("Enter email: ", loop=self.loop)

                        if not email:
                            continue

                        confirm = await ainput(f'Is "{email}" correct? (y/N): ', loop=self.loop)

                        if confirm.lower() == "y":
                            break

                    await self.invoke(
                        raw.functions.account.SendVerifyEmailCode(
                            purpose=raw.types.EmailVerifyPurposeLoginSetup(
                                phone_number=self.phone_number,
                                phone_code_hash=sent_code.phone_code_hash,
                            ),
                            email=email,
                        )
                    )

                    email_code = await ainput("Enter confirmation code: ", loop=self.loop)

                    email_sent_code = await self.invoke(
                        raw.functions.account.VerifyEmail(
                            purpose=raw.types.EmailVerifyPurposeLoginSetup(
                                phone_number=self.phone_number,
                                phone_code_hash=sent_code.phone_code_hash,
                            ),
                            verification=raw.types.EmailVerificationCode(code=email_code),
                        )
                    )

                    if isinstance(email_sent_code, raw.types.account.EmailVerifiedLogin):
                        if isinstance(email_sent_code.sent_code, raw.types.auth.SentCodePaymentRequired):
                            # TODO: raw.functions.auth.CheckPaidAuth
                            raise Unauthorized(
                                f"You need to pay {email_sent_code.sent_code.amount}{email_sent_code.sent_code.currency} or purchase premium to continue authorization "
                                "process, which is currently not supported by Pyrogram."
                            )
                except BadRequest as e:
                    print(e.MESSAGE)
                else:
                    break
        else:
            sent_code_descriptions = {
                enums.SentCodeType.APP: "Telegram app",
                enums.SentCodeType.SMS: "SMS",
                enums.SentCodeType.CALL: "phone call",
                enums.SentCodeType.FLASH_CALL: "phone flash call",
                enums.SentCodeType.FRAGMENT_SMS: "Fragment",
                enums.SentCodeType.EMAIL_CODE: "email code",
                enums.SentCodeType.MISSED_CALL: "missed call",
                enums.SentCodeType.FIREBASE_SMS: "Firebase SMS",
                enums.SentCodeType.SMS_PHRASE: "SMS phrase",
                enums.SentCodeType.SMS_WORD: "SMS word"
            }

            print(f"The confirmation code has been sent via {sent_code_descriptions.get(sent_code.type, str(sent_code.type))}")

        while True:
            if not self.phone_code:
                self.phone_code = await ainput("Enter confirmation code: ", loop=self.loop)

            try:
                sign_in_result = await self.sign_in(self.phone_number, sent_code.phone_code_hash, self.phone_code)
            except BadRequest as e:
                print(e.MESSAGE)
                self.phone_code = None
            except SessionPasswordNeeded as e:
                print(e.MESSAGE)
                return await self._handle_2fa_password()
            else:
                break

        if isinstance(sign_in_result, User):
            return sign_in_result

        terms_of_service = sign_in_result if isinstance(sign_in_result, TermsOfService) else None

        while True:
            first_name = await ainput("Enter first name: ", loop=self.loop)
            last_name = await ainput("Enter last name (empty to skip): ", loop=self.loop)

            try:
                signed_up = await self.sign_up(
                    self.phone_number,
                    sent_code.phone_code_hash,
                    first_name,
                    last_name
                )
            except BadRequest as e:
                print(e.MESSAGE)
            else:
                break

        if terms_of_service:
            print("\n" + terms_of_service.text + "\n")
            await self.accept_terms_of_service(terms_of_service.id)

        return signed_up

    async def authorize_qr(self, except_ids: Optional[List[int]] = None) -> "User":
        from qrcode import QRCode

        qr_login = QRLogin(self, except_ids or [])
        await qr_login.recreate()

        qr = QRCode(version=1)

        while True:
            try:
                print(
                    "\x1b[2J\n"
                    f"Welcome to Pyrogram (version {__version__})\n"
                    "Pyrogram is free software and comes with ABSOLUTELY NO WARRANTY. Licensed\n"
                    f"under the terms of the {__license__}.\n"
                    "Scan the QR code below to login\n"
                    "Settings -> Privacy and Security -> Active Sessions -> Scan QR Code.",
                    flush=True
                )

                qr.clear()
                qr.add_data(qr_login.url)
                qr.print_ascii(tty=True)
                log.info("Waiting for QR code being scanned.")

                signed_in = await qr_login.wait()

                if signed_in:
                    log.info("Logged in successfully as %s", signed_in.full_name)
                    return signed_in

                log.info("QR login returned no user, retrying.")
                await qr_login.recreate()
            except asyncio.TimeoutError:
                log.info("Recreating QR code.")
                await qr_login.recreate()
            except AuthTokenExpired:
                log.info("Auth token expired. Recreating QR code.")
                await qr_login.recreate()
            except SessionPasswordNeeded as e:
                print(e.MESSAGE)
                return await self._handle_2fa_password()

    def set_parse_mode(self, parse_mode: Optional["enums.ParseMode"]):
        """Set the parse mode to be used globally by the client.

        When setting the parse mode with this method, all other methods having a *parse_mode* parameter will follow the
        global value by default.

        Parameters:
            parse_mode (:obj:`~pyrogram.enums.ParseMode`):
                By default, texts are parsed using both Markdown and HTML styles.
                You can combine both syntaxes together.

        Example:
            .. code-block:: python

                from pyrogram import enums

                # Default combined mode: Markdown + HTML
                await app.send_message("me", "1. **markdown** and <i>html</i>")

                # Force Markdown-only, HTML is disabled
                app.set_parse_mode(enums.ParseMode.MARKDOWN)
                await app.send_message("me", "2. **markdown** and <i>html</i>")

                # Force HTML-only, Markdown is disabled
                app.set_parse_mode(enums.ParseMode.HTML)
                await app.send_message("me", "3. **markdown** and <i>html</i>")

                # Disable the parser completely
                app.set_parse_mode(enums.ParseMode.DISABLED)
                await app.send_message("me", "4. **markdown** and <i>html</i>")

                # Bring back the default combined mode
                app.set_parse_mode(enums.ParseMode.DEFAULT)
                await app.send_message("me", "5. **markdown** and <i>html</i>")
        """

        self.parse_mode = parse_mode

    async def _handle_2fa_password(self) -> User:
        while True:
            print("Password hint: {}".format(await self.get_password_hint()))

            if not self.password:
                self.password = await ainput(
                    "Enter 2FA password (empty to recover): ",
                    hide=self.hide_password,
                    loop=self.loop
                )

            try:
                if not self.password:
                    confirm = await ainput("Confirm password recovery (y/N): ", loop=self.loop)

                    if confirm.lower() == "y":
                        email_pattern = await self.send_recovery_code()
                        print(f"The recovery code has been sent to {email_pattern}")

                        while True:
                            recovery_code = await ainput("Enter recovery code: ", loop=self.loop)

                            try:
                                return await self.recover_password(recovery_code)
                            except BadRequest as e:
                                print(e.MESSAGE)
                            except Exception:
                                log.exception("Unexpected error during password recovery")
                                raise
                    else:
                        self.password = None
                else:
                    return await self.check_password(self.password)
            except BadRequest as e:
                print(e.MESSAGE)
                self.password = None

    async def fetch_peers(self, peers: List[Union[raw.types.User, raw.types.Chat, raw.types.Channel]]) -> bool:
        is_min = False
        parsed_peers = []
        parsed_usernames = []

        for peer in peers:
            if getattr(peer, "min", False):
                is_min = True
                continue

            usernames = []
            phone_number = None

            if isinstance(peer, raw.types.User):
                peer_id = peer.id
                access_hash = peer.access_hash
                phone_number = peer.phone
                peer_type = "bot" if peer.bot else "user"

                if peer.usernames:
                    usernames.extend(u.username.lower() for u in peer.usernames)
                elif peer.username:
                    usernames.append(peer.username.lower())
            elif isinstance(peer, (raw.types.Chat, raw.types.ChatForbidden)):
                peer_id = -peer.id
                access_hash = 0
                peer_type = "group"
            elif isinstance(peer, raw.types.Channel):
                peer_id = utils.get_channel_id(peer.id)
                access_hash = peer.access_hash
                peer_type = "direct" if peer.monoforum else "channel" if peer.broadcast else "forum" if peer.forum else "supergroup"

                if peer.usernames:
                    usernames.extend(u.username.lower() for u in peer.usernames)
                elif peer.username:
                    usernames.append(peer.username.lower())
            elif isinstance(peer, raw.types.ChannelForbidden):
                peer_id = utils.get_channel_id(peer.id)
                access_hash = peer.access_hash
                peer_type = "channel" if peer.broadcast else "supergroup"
            else:
                continue

            parsed_peers.append((peer_id, access_hash, peer_type, phone_number))

            if usernames:
                parsed_usernames.append((peer_id, usernames))

        await self.storage.update_peers(parsed_peers)

        if parsed_usernames:
            await self.storage.update_usernames(parsed_usernames)

        return is_min

    async def handle_updates(self, updates):
        self.last_update_time = datetime.now()
        self._last_update_monotonic = time.monotonic()

        def _enqueue_update(item):
            try:
                self.dispatcher.updates_queue.put_nowait(item)
            except asyncio.QueueFull:
                log.warning("Update queue full (%d), dropping update",
                            self.dispatcher.updates_queue.maxsize)

        if isinstance(updates, (raw.types.Updates, raw.types.UpdatesCombined)):
            is_min_users = await self.fetch_peers(updates.users)
            is_min_chats = await self.fetch_peers(updates.chats)
            is_min = is_min_users or is_min_chats

            if isinstance(updates, raw.types.UpdatesCombined):
                seq_start = getattr(updates, "seq_start", updates.seq)
                stored_states = await self.storage.update_state()
                if stored_states:
                    global_state = next((s for s in stored_states if s[0] == 0), None)
                    if global_state and global_state[4] is not None:
                        stored_seq = global_state[4]
                        if seq_start > stored_seq + 1:
                            log.warning(
                                "Seq gap detected: stored=%s, seq_start=%s. Triggering recovery.",
                                stored_seq, seq_start
                            )
                            await self.recover_gaps()

            users = {u.id: u for u in updates.users}
            chats = {c.id: c for c in updates.chats}

            for update in updates.updates:
                channel_id = getattr(
                    getattr(
                        getattr(
                            update, "message", None
                        ), "peer_id", None
                    ), "channel_id", None
                ) or getattr(update, "channel_id", None)

                pts = getattr(update, "pts", None)
                pts_count = getattr(update, "pts_count", None)

                if pts:
                    await self.storage.update_state(
                        (
                            utils.get_channel_id(channel_id) if channel_id else 0,
                            pts,
                            None,
                            updates.date,
                            updates.seq
                        )
                    )

                if isinstance(update, raw.types.UpdateChannelTooLong):
                    log.info("UpdateChannelTooLong: %s", update)

                if isinstance(update, raw.types.UpdateNewChannelMessage) and is_min:
                    message = update.message

                    if not isinstance(message, raw.types.MessageEmpty) and pts and pts_count:
                        try:
                            diff = await self.invoke(
                                raw.functions.updates.GetChannelDifference(
                                    channel=await self.resolve_peer(utils.get_channel_id(channel_id)),
                                    filter=raw.types.ChannelMessagesFilter(
                                        ranges=[raw.types.MessageRange(
                                            min_id=update.message.id,
                                            max_id=update.message.id
                                        )]
                                    ),
                                    pts=pts - pts_count,
                                    limit=pts,
                                    force=False
                                )
                            )
                        except (ChannelPrivate, PersistentTimestampOutdated, PersistentTimestampInvalid):
                            pass
                        else:
                            if not isinstance(diff, raw.types.updates.ChannelDifferenceEmpty):
                                users.update({u.id: u for u in diff.users})
                                chats.update({c.id: c for c in diff.chats})

                _enqueue_update((update, users, chats))
        elif isinstance(updates, (raw.types.UpdateShortMessage, raw.types.UpdateShortChatMessage)):
            await self.storage.update_state(
                (
                    0,
                    updates.pts,
                    None,
                    updates.date,
                    None
                )
            )

            diff = await self.invoke(
                raw.functions.updates.GetDifference(
                    pts=updates.pts - updates.pts_count,
                    date=updates.date,
                    qts=-1
                )
            )

            if isinstance(diff, (raw.types.updates.DifferenceEmpty, raw.types.updates.DifferenceTooLong)):
                pass
            elif getattr(diff, "new_messages", None):
                _enqueue_update((
                    raw.types.UpdateNewMessage(
                        message=diff.new_messages[0],
                        pts=updates.pts,
                        pts_count=updates.pts_count
                    ),
                    {u.id: u for u in diff.users},
                    {c.id: c for c in diff.chats}
                ))
            elif getattr(diff, "other_updates", None):
                _enqueue_update((diff.other_updates[0], {}, {}))
        elif isinstance(updates, raw.types.UpdateShort):
            _enqueue_update((updates.update, {}, {}))
        elif isinstance(updates, raw.types.UpdatesTooLong):
            log.info("UpdatesTooLong: %s", updates)

    async def load_session(self):
        await self.storage.open()

        session_empty = (
            await self.storage.test_mode() is None
            or await self.storage.auth_key() is None
            or await self.storage.user_id() is None
            or await self.storage.is_bot() is None
        )

        if session_empty:
            if not self.api_id or not self.api_hash:
                raise AttributeError("The API key is required for new authorizations. "
                                     "More info: https://docs.pyrogram.org/start/auth")

            await self.storage.api_id(self.api_id)

            await self.storage.dc_id(2)

            if self.test_mode:
                await self.storage.server_address("2001:67c:4e8:f002::e" if self.ipv6 else "149.154.167.40")
                await self.storage.port(80)
            else:
                await self.storage.server_address("2001:67c:4e8:f002::a" if self.ipv6 else "149.154.167.51")
                await self.storage.port(443)

            await self.storage.date(0)

            await self.storage.test_mode(self.test_mode)
            await self.storage.auth_key(
                await Auth(
                    self,
                    await self.storage.dc_id(),
                    await self.storage.server_address(),
                    await self.storage.port(),
                    await self.storage.test_mode()
                ).create()
            )
            await self.storage.user_id(None)
            await self.storage.is_bot(None)
        else:
            # Needed for migration from storage v2 to v3
            if not await self.storage.api_id():
                if self.api_id:
                    await self.storage.api_id(self.api_id)
                else:
                    while True:
                        try:
                            value = int(await ainput("Enter the api_id part of the API key: ", loop=self.loop))

                            if value <= 0:
                                print("Invalid value")
                                continue

                            confirm = await ainput(f'Is "{value}" correct? (y/N): ', loop=self.loop)

                            if confirm.lower() == "y":
                                await self.storage.api_id(value)
                                break
                        except Exception as e:
                            print(e)

    def load_plugins(self):
        if self.plugins:
            plugins = self.plugins.copy()

            for option in ["include", "exclude"]:
                if plugins.get(option, []):
                    plugins[option] = [
                        (i.split()[0], i.split()[1:] or None)
                        for i in self.plugins[option]
                    ]
        else:
            return

        if plugins.get("enabled", True):
            root = plugins["root"]
            include = plugins.get("include", [])
            exclude = plugins.get("exclude", [])

            if isinstance(root, list):
                roots = root
            else:
                roots = [root]

            count = 0

            for root in roots:
                plugin_path = Path(root.replace(".", "/"))
                if ".." in plugin_path.parts or plugin_path.is_absolute():
                    log.warning('[%s] [LOAD] Skipping suspicious plugin path "%s"', self.name, root)
                    continue

                if not include:
                    for path in sorted(Path(root.replace(".", "/")).rglob("*.py")):
                        module_path = '.'.join(path.parent.parts + (path.stem,))
                        module = import_module(module_path)

                        for name in vars(module).keys():
                            # noinspection PyBroadException
                            try:
                                for handler, group in getattr(module, name).handlers:
                                    if isinstance(handler, Handler) and isinstance(group, int):
                                        self.add_handler(handler, group)

                                        log.info('[{}] [LOAD] {}("{}") in group {} from "{}"'.format(
                                            self.name, type(handler).__name__, name, group, module_path))

                                        count += 1
                            except Exception:
                                pass
                else:
                    for path, handlers in include:
                        if ".." in path.split("."):
                            log.warning('[%s] [LOAD] Skipping suspicious include path "%s"', self.name, path)
                            continue

                        module_path = root + "." + path
                        warn_non_existent_functions = True

                        try:
                            module = import_module(module_path)
                        except ImportError:
                            log.warning('[%s] [LOAD] Ignoring non-existent module "%s"', self.name, module_path)
                            continue

                        if "__path__" in dir(module):
                            log.warning('[%s] [LOAD] Ignoring namespace "%s"', self.name, module_path)
                            continue

                        if handlers is None:
                            handlers = vars(module).keys()
                            warn_non_existent_functions = False

                        for name in handlers:
                            # noinspection PyBroadException
                            try:
                                for handler, group in getattr(module, name).handlers:
                                    if isinstance(handler, Handler) and isinstance(group, int):
                                        self.add_handler(handler, group)

                                        log.info('[{}] [LOAD] {}("{}") in group {} from "{}"'.format(
                                            self.name, type(handler).__name__, name, group, module_path))

                                        count += 1
                            except Exception:
                                if warn_non_existent_functions:
                                    log.warning('[{}] [LOAD] Ignoring non-existent function "{}" from "{}"'.format(
                                        self.name, name, module_path))

                if exclude:
                    for path, handlers in exclude:
                        if ".." in path.split("."):
                            log.warning('[%s] [UNLOAD] Skipping suspicious exclude path "%s"', self.name, path)
                            continue

                        module_path = root + "." + path
                        warn_non_existent_functions = True

                        try:
                            module = import_module(module_path)
                        except ImportError:
                            log.warning('[%s] [UNLOAD] Ignoring non-existent module "%s"', self.name, module_path)
                            continue

                        if "__path__" in dir(module):
                            log.warning('[%s] [UNLOAD] Ignoring namespace "%s"', self.name, module_path)
                            continue

                        if handlers is None:
                            handlers = vars(module).keys()
                            warn_non_existent_functions = False

                        for name in handlers:
                            # noinspection PyBroadException
                            try:
                                for handler, group in getattr(module, name).handlers:
                                    if isinstance(handler, Handler) and isinstance(group, int):
                                        self.remove_handler(handler, group)

                                        log.info('[{}] [UNLOAD] {}("{}") from group {} in "{}"'.format(
                                            self.name, type(handler).__name__, name, group, module_path))

                                        count -= 1
                            except Exception:
                                if warn_non_existent_functions:
                                    log.warning('[{}] [UNLOAD] Ignoring non-existent function "{}" from "{}"'.format(
                                        self.name, name, module_path))

            if count > 0:
                log.info('[{}] Successfully loaded {} plugin{} from "{}"'.format(
                    self.name, count, "s" if count > 1 else "", ", ".join(roots)))
            else:
                log.warning('[%s] No plugin loaded from "%s"', self.name, ", ".join(roots))

    async def handle_download(self, packet):
        file_id, directory, file_name, in_memory, file_size, progress, progress_args = packet

        file_name = os.path.basename(file_name.replace("\\", "/"))
        loop = asyncio.get_running_loop()
        if not in_memory:
            await loop.run_in_executor(None, lambda: os.makedirs(directory, exist_ok=True))

        temp_file_path = os.path.abspath(os.path.join(directory, file_name)) + ".temp"
        file = BytesIO() if in_memory else await loop.run_in_executor(None, lambda: open(temp_file_path, "wb"))
        success = False

        try:
            async for chunk in self.get_file(file_id, file_size, 0, 0, progress, progress_args):
                if in_memory:
                    file.write(chunk)
                else:
                    await loop.run_in_executor(None, file.write, chunk)
            success = True
        except (asyncio.CancelledError, FloodWaitX, FloodPremiumWaitX):
            raise
        except Exception:
            log.exception("Download failed")
            return None
        finally:
            if not success and not in_memory:
                await loop.run_in_executor(None, file.close)
                with suppress(OSError):
                    await loop.run_in_executor(None, os.remove, temp_file_path)

        if in_memory:
            file.name = file_name
            return file

        await loop.run_in_executor(None, file.close)
        file_path = os.path.splitext(temp_file_path)[0]
        await loop.run_in_executor(None, shutil.move, temp_file_path, file_path)
        return file_path

    async def get_file(
        self,
        file_id: FileId,
        file_size: int = 0,
        limit: int = 0,
        offset: int = 0,
        progress: Callable = None,
        progress_args: tuple = ()
    ) -> AsyncGenerator[bytes, None]:
        async with self.get_file_semaphore:
            file_type = file_id.file_type

            if file_type == FileType.CHAT_PHOTO:
                if file_id.chat_id > 0:
                    peer = raw.types.InputPeerUser(
                        user_id=file_id.chat_id,
                        access_hash=file_id.chat_access_hash
                    )
                else:
                    if file_id.chat_access_hash == 0:
                        peer = raw.types.InputPeerChat(
                            chat_id=-file_id.chat_id
                        )
                    else:
                        peer = raw.types.InputPeerChannel(
                            channel_id=utils.get_channel_id(file_id.chat_id),
                            access_hash=file_id.chat_access_hash
                        )

                location = raw.types.InputPeerPhotoFileLocation(
                    peer=peer,
                    photo_id=file_id.media_id,
                    big=file_id.thumbnail_source == ThumbnailSource.CHAT_PHOTO_BIG
                )
            elif file_type == FileType.PHOTO:
                location = raw.types.InputPhotoFileLocation(
                    id=file_id.media_id,
                    access_hash=file_id.access_hash,
                    file_reference=file_id.file_reference,
                    thumb_size=file_id.thumbnail_size
                )
            else:
                location = raw.types.InputDocumentFileLocation(
                    id=file_id.media_id,
                    access_hash=file_id.access_hash,
                    file_reference=file_id.file_reference,
                    thumb_size=file_id.thumbnail_size
                )

            current = 0
            total = abs(limit) or (1 << 31) - 1
            chunk_size = 1024 * 1024
            offset_bytes = abs(offset) * chunk_size

            dc_id = file_id.dc_id

            try:
                session = await self.get_session(dc_id, is_media=True)

                r = await session.invoke(
                    raw.functions.upload.GetFile(
                        location=location,
                        offset=offset_bytes,
                        limit=chunk_size
                    ),
                    sleep_threshold=30
                )

                if isinstance(r, raw.types.upload.File):
                    while True:
                        chunk = r.bytes

                        yield chunk

                        current += 1
                        offset_bytes += chunk_size

                        if progress:
                            await invoke_callable(
                                progress,
                                min(offset_bytes, file_size) if file_size != 0 else offset_bytes,
                                file_size,
                                *progress_args,
                                executor=self.executor,
                                loop=self.loop
                            )

                        if len(chunk) < chunk_size or current >= total:
                            break

                        r = await session.invoke(
                            raw.functions.upload.GetFile(
                                location=location,
                                offset=offset_bytes,
                                limit=chunk_size
                            ),
                            sleep_threshold=30
                        )

                elif isinstance(r, raw.types.upload.FileCdnRedirect):

                    cdn_session = await self.get_session(dc_id, is_cdn=True, temporary=True)

                    try:
                        while True:
                            r2 = await cdn_session.invoke(
                                raw.functions.upload.GetCdnFile(
                                    file_token=r.file_token,
                                    offset=offset_bytes,
                                    limit=chunk_size
                                )
                            )

                            if isinstance(r2, raw.types.upload.CdnFileReuploadNeeded):
                                try:
                                    await session.invoke(
                                        raw.functions.upload.ReuploadCdnFile(
                                            file_token=r.file_token,
                                            request_token=r2.request_token
                                        )
                                    )
                                except (FileTokenInvalid, RequestTokenInvalid):
                                    break
                                else:
                                    continue

                            chunk = r2.bytes

                            # https://core.telegram.org/cdn#decrypting-files
                            decrypted_chunk = await self.loop.run_in_executor(  # type: ignore[arg-type]
                                self.executor,
                                aes.ctr256_decrypt,
                                chunk,   # type: ignore[arg-type]
                                r.encryption_key,  # type: ignore[arg-type]
                                bytearray(r.encryption_iv[:-4] + (offset_bytes // 16).to_bytes(4, "big"))  # type: ignore[arg-type]
                            )

                            hashes = await session.invoke(
                                raw.functions.upload.GetCdnFileHashes(
                                    file_token=r.file_token,
                                    offset=offset_bytes
                                )
                            )

                            # https://core.telegram.org/cdn#verifying-files
                            def _check_all_hashes():
                                for h in hashes:
                                    cdn_chunk = decrypted_chunk[h.offset - offset_bytes: h.offset - offset_bytes + h.limit]
                                    CDNFileHashMismatch.check(
                                        h.hash == sha256(cdn_chunk).digest(),
                                        "h.hash == sha256(cdn_chunk).digest()"
                                    )

                            await self.loop.run_in_executor(self.executor, _check_all_hashes)

                            yield decrypted_chunk

                            current += 1
                            offset_bytes += chunk_size

                            if progress:
                                await invoke_callable(
                                    progress,
                                    min(offset_bytes, file_size) if file_size != 0 else offset_bytes,
                                    file_size,
                                    *progress_args,
                                    executor=self.executor,
                                    loop=self.loop
                                )

                            if len(chunk) < chunk_size or current >= total:
                                break
                    finally:
                        await cdn_session.stop()
            except pyrogram.StopTransmission:
                raise
            except (FloodWaitX, FloodPremiumWaitX):
                raise
            except Exception:
                log.exception("get_file error")
                raise

    async def get_session(
        self,
        dc_id: Optional[int] = None,
        is_media: Optional[bool] = False,
        is_cdn: Optional[bool] = False,
        business_connection_id: Optional[str] = None,
        export_authorization: Optional[bool] = True,
        server_address: Optional[str] = None,
        port: Optional[int] = None,
        temporary: Optional[bool] = False
    ) -> "Session":
        """Get existing session or create a new one.

        Parameters:
            dc_id (``int``, *optional*):
                Datacenter identifier.

            is_media (``bool``, *optional*):
                Pass True to get or create a media session.

            is_cdn (``bool``, *optional*):
                Pass True to get or create a cdn session.

            business_connection_id (``str``, *optional*):
                Business connection identifier.

            export_authorization (``bool``, *optional*):
                Pass True to export authorization after creating the session.
                Used only when creating a new session.

            server_address (``str``, *optional*):
                Custom server address to connect to.
                Used only when creating a new session.

            port (``int``, *optional*):
                Custom port to connect to.
                Used only when creating a new session.

            temporary (``bool``, *optional*):
                Create temporary session instead of getting from storage.
                Used only when uploading/downloading and don't forget to stop it.
        """
        if not dc_id:
            dc_id = await self.storage.dc_id()

        if business_connection_id:
            dc_id = self.business_connections.get(business_connection_id)

            if dc_id is None:
                connection = await self.session.invoke(
                    raw.functions.account.GetBotBusinessConnection(
                        connection_id=business_connection_id
                    )
                )

                if not connection.updates:
                    raise ValueError(f"No updates returned for business connection {business_connection_id}")

                dc_id = self.business_connections[business_connection_id] = connection.updates[0].connection.dc_id

        is_current_dc = await self.storage.dc_id() == dc_id

        if not temporary and is_current_dc and not is_media:
            return self.session

        sessions = self.media_sessions if is_media else self.sessions
        session_key = (dc_id, is_media)

        creator = False

        if not temporary:
            async with self.sessions_lock:
                if sessions.get(dc_id):
                    return sessions[dc_id]

                pending_session = self._session_futures.get(session_key)

                if pending_session is None:
                    pending_session = self.loop.create_future()
                    pending_session.add_done_callback(
                        lambda future: None if future.cancelled() else future.exception()
                    )
                    self._session_futures[session_key] = pending_session
                    creator = True

            if not creator:
                return await pending_session

        session = None

        try:
            if not server_address or not port:
                dc_option = await self.get_dc_option(dc_id, is_media=is_media, ipv6=self.ipv6, is_cdn=is_cdn)

                server_address = server_address or dc_option.ip_address
                port = port or dc_option.port

            if is_media:
                auth_key = (await self.get_session(dc_id)).auth_key
            else:
                if not is_current_dc:
                    auth_key = await Auth(
                        self,
                        dc_id,
                        server_address,
                        port,
                        await self.storage.test_mode()
                    ).create()
                else:
                    auth_key = await self.storage.auth_key()

            session = Session(
                self,
                dc_id,
                server_address,
                port,
                auth_key,
                await self.storage.test_mode(),
                is_media=is_media
            )

            await session.start()

            try:
                await asyncio.wait_for(session.is_started.wait(), Session.WAIT_TIMEOUT)
            except asyncio.TimeoutError as e:
                with suppress(Exception):
                    await session.stop()
                session = None
                raise ConnectionError(f"Failed to start session for DC{dc_id}") from e

            if not is_current_dc and export_authorization:
                for _ in range(3):
                    exported_auth = await self.invoke(
                        raw.functions.auth.ExportAuthorization(
                            dc_id=dc_id
                        )
                    )

                    try:
                        await session.invoke(
                            raw.functions.auth.ImportAuthorization(
                                id=exported_auth.id,
                                bytes=exported_auth.bytes
                            )
                        )
                    except AuthBytesInvalid:
                        continue
                    else:
                        break
                else:
                    await session.stop()
                    session = None
                    raise AuthBytesInvalid

            if not temporary:
                async with self.sessions_lock:
                    cached_session = sessions.get(dc_id)

                    if cached_session is None:
                        sessions[dc_id] = session
                    else:
                        with suppress(Exception):
                            await session.stop()
                        session = cached_session

                    pending_session = self._session_futures.pop(session_key, None)

                    if pending_session is not None and not pending_session.done():
                        pending_session.set_result(session)
        except Exception as e:
            if session is not None:
                with suppress(Exception):
                    await session.stop()

            if not temporary:
                async with self.sessions_lock:
                    pending_session = self._session_futures.pop(session_key, None)

                    if pending_session is not None and not pending_session.done():
                        pending_session.set_exception(e)

            raise

        return session

    async def get_dc_option(
        self,
        dc_id: int = None,
        is_media: bool = False,
        is_cdn: bool = False,
        ipv6: bool = False
    ) -> "raw.types.DcOption":
        if self.__config is None:
            self.__config = await self.invoke(raw.functions.help.GetConfig())

        if dc_id is None:
            dc_id = self.__config.this_dc

        options = [dc for dc in self.__config.dc_options if dc.id == dc_id and dc.ipv6 == ipv6] # type: List[raw.types.DcOption]

        if not options:
            raise ValueError(f"DC{dc_id} not found")

        if is_cdn:
            cdn_options = [dc for dc in options if dc.cdn]

            if cdn_options:
                return cdn_options[0]

            log.debug(
                "No CDN datacenter found for DC%s, falling back to media DC",
                dc_id
            )

            is_media = True

        if is_media:
            media_options = [dc for dc in options if dc.media_only]

            if media_options:
                return media_options[0]

            log.debug(
                "No media datacenter found for DC%s, falling back to prod DC",
                dc_id
            )

        prod_options = [dc for dc in options if not dc.media_only]

        if prod_options:
            # Internal low-latency selection (no public configuration)
            try:
                best = await select_best_dc_option(
                    self,
                    dc_id,
                    prod_options,
                    is_media=is_media,
                    is_cdn=is_cdn,
                    ipv6=ipv6,
                )
                if best is not None:
                    return best
            except Exception as e:
                log.info("Endpoint selection failed: %s %s", type(e).__name__, e)
            return prod_options[0]

        raise ValueError("No suitable DC found")

    async def set_dc(
        self,
        dc_id: Optional[int] = None,
        server_address: Optional[str] = None,
        port: Optional[int] = None
    ):
        """Set configuration for the specified datacenter.

        .. note::

            Be careful with this method, you can easily break your session.

        Parameters:
            dc_id (``int``, *optional*):
                Datacenter identifier.
                Defaults to the current datacenter.

            server_address (``str``, *optional*):
                Custom server address.

            port (``int``, *optional*):
                Custom port.
        """
        if not self.__config:
            self.__config = await self.invoke(raw.functions.help.GetConfig())

        dc_id = dc_id or self.__config.this_dc
        dc_option = await self.get_dc_option(dc_id, ipv6=self.ipv6)

        server_address = server_address or dc_option.ip_address
        port = port or dc_option.port

        await self.storage.dc_id(dc_id)
        await self.storage.server_address(server_address)
        await self.storage.port(port)

        if self.session is None:
            return

        if self.session.server_address != server_address or self.session.port != port:
            self.session.server_address = server_address
            self.session.port = port

            await self.session.restart()
            log.info("Changed session DC%s address to %s:%s", dc_id, server_address, port)
        else:
            log.info("Session DC%s address is already %s:%s", dc_id, server_address, port)

    @property
    def server_time(self) -> float:
        return time.time() + self._server_time_offset

    def _set_server_time(self, msg_id: int):
        server_ts = msg_id / float(2**32)
        self._server_time_offset = server_ts - time.time()
        log.info("Time synced: offset=%.3fs, server_time=%s", self._server_time_offset, utils.timestamp_to_datetime(server_ts))

    def guess_mime_type(self, filename: Union[str, BytesIO]) -> Optional[str]:
        if isinstance(filename, BytesIO):
            return self.mimetypes.guess_type(filename.name)[0]

        return self.mimetypes.guess_type(filename)[0]

    def guess_extension(self, mime_type: str) -> Optional[str]:
        return self.mimetypes.guess_extension(mime_type)


class Cache:
    """LRU cache backed by OrderedDict.

    Note: ``__getitem__`` returns ``None`` for missing keys instead of raising
    ``KeyError``.  All existing call-sites rely on this behaviour.
    """

    def __init__(self, capacity: int):
        self.capacity = capacity
        self.store = OrderedDict()

    def get(self, key, default=None):
        try:
            self.store.move_to_end(key)
            return self.store[key]
        except KeyError:
            return default

    def __getitem__(self, key):
        return self.get(key)

    def __setitem__(self, key, value):
        if self.capacity == 0:
            return

        try:
            self.store.move_to_end(key)
        except KeyError:
            if len(self.store) >= self.capacity:
                self.store.popitem(last=False)
        self.store[key] = value

    def __contains__(self, key):
        return key in self.store
