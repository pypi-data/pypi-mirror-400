# Copyright 2026 zovdev
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import sys
import inspect
import asyncio
import msgpack

from Ncore.session import Session



class BaseClient:
    def info(self, txt):
        sys.stdout.write(f"\033[1;34m[ INFO ] [ {inspect.currentframe().f_back.f_code.co_name} ] {txt}\033[0m\n")

    def warn(self, txt):
        sys.stdout.write(f"\033[1;33m[ WARN ] [ {inspect.currentframe().f_back.f_code.co_name} ] {txt}\033[0m\n")

    def error(self, txt):
        sys.stdout.write(f"\033[1;31m[ ERROR ] [ {inspect.currentframe().f_back.f_code.co_name} ] {txt}\033[0m\n")

    def __init__(self, api_id, api_hash, bot_token, storagename="storage", loop=None):
        if not isinstance(loop, asyncio.AbstractEventLoop):
            try:
                loop = asyncio.get_running_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)

        self.api_id = api_id
        self.api_hash = api_hash
        self.bot_token = bot_token
        self.storagename = storagename
        self.loop = loop

        self.routers = {}

        self.storage = {
            "id": None,
            "first_name": None,
            "username": None,
            "dc_id": 2,
            "auth_key": None,
        }

        try:
            if self.storagename:
                self.storage = msgpack.load(open(self.storagename, "rb"))
                self.info(f"Сессия [{self.storagename}] загружена")
            else:
                self.info("Сессия [:memory:] загружена")
        except:
            self.save_storage()

        self.session = Session(self, self.loop)

    def save_storage(self):
        if not self.storagename:
            return
        try:
            msgpack.dump(self.storage, open(self.storagename, "wb"))
        except BaseException as ex:
            self.error(f"Ошибка сохранения сессии [{self.storagename}] -> {ex}")

    async def start(self, handle_updates=None, device_model="Ncore python", system_version="10.0", app_version="4.0", system_lang_code="ru", lang_pack="tdesktop", lang_code="ru"):
        await self.session.start(device_model, system_version, app_version, system_lang_code, lang_pack, lang_code)
        await self.session.invoke({"_": "getState"})

        if handle_updates is not None:
            self.handle_updates = handle_updates

    async def handle_updates(self, message):
        # TODO добавить pre_middleware
        self.info(message) # TODO добавить обработчики
        # TODO добавить post_middleware