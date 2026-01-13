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

import os
import time
import struct
import socket
import asyncio
from tkinter import NO
import tgcrypto

from io import BytesIO
from hashlib import sha1, sha256
from concurrent.futures import ThreadPoolExecutor

from Ncore.utils import MsgFactory, Auth
from Ncore.tl_object import CoreMessage


BADMSGNOTIFICATIONS = {
    16: "Не верный msg_id, требуется синхронизация времени.",
    17: "Не верный msg_id, требуется синхронизация времени.",
    18: "Не верный msg_id, клиентский msg_id должен быть кратен 4.",
    19: "Не верный msg_id, msg_id контейнера == msg_id предыдущего сообщения.",
    20: "Очень старое сообщение.",
    32: "Не верный msg_seqno.",
    33: "Не верный msg_seqno.",
    34: "Не верный msg_seqno, отправленно нечетное значение.",
    35: "Не верный msg_seqno, получено четное значение.",
    48: "Неправильная соль сервера.",
    64: "Недопустимый контейнер."
}


class Connect:
    def __init__(self, client, loop):
        self.client = client
        self.loop = loop

        self._state = 0
        self._isAuth = 0

        if not self.client.storage["auth_key"]:
            self.client.warn("Получение auth_key")
            self.loop.run_until_complete(Auth(self.client, self.loop, self)())
            self._isAuth = 1
            self.client.info("Получен auth_key")

        self.salt = 0
        self.session_id = os.urandom(8)
        self.auth_key = self.client.storage["auth_key"]
        self.auth_key_id = sha1(self.auth_key).digest()[-8:]

    def kdf(self, msg_key, x):
        sha256_a = sha256(msg_key + self.auth_key[x:x+36]).digest()
        sha256_b = sha256(self.auth_key[x+40:x+76] + msg_key).digest()
        return sha256_a[:8] + sha256_b[8:24] + sha256_a[24:32], sha256_b[:8] + sha256_a[8:24] + sha256_b[24:32]

    def pack(self, message):
        data = struct.pack("<Q", self.salt) + self.session_id + message.write()

        padding_len = 16 - (len(data) % 16)
        if padding_len < 12:
            padding_len += 16
        padding = os.urandom(padding_len)

        msg_key = sha256(self.auth_key[88:120] + data + padding).digest()[8:24]
        aes_key, aes_iv = self.kdf(msg_key, 0)

        return self.auth_key_id + msg_key + tgcrypto.ige256_encrypt(data + padding, aes_key, aes_iv)


    def unpack(self, data):
        if data[0:8] != self.auth_key_id:
            raise ValueError("Ошибка безопасности не верный auth_key_id")

        msg_key = data[8:24]
        aes_key, aes_iv = self.kdf(msg_key, 8)
        decrypted_data = tgcrypto.ige256_decrypt(data[24:], aes_key, aes_iv)
        data = decrypted_data[8:]

        if data[0:8] != self.session_id:
            raise ValueError("Ошибка безопасности не верный session_id")
        if msg_key != sha256(self.auth_key[96:128] + decrypted_data).digest()[8:24]:
            raise ValueError("Ошибка безопасности не верный msg_key")

        message = CoreMessage.read(BytesIO(data[8:]))

        payload_len = len(decrypted_data) - 32

        if not 12 <= (payload_len - message.length) <= 1024:
            raise ValueError("Ошибка безопасности не верный length padding")
        if not payload_len % 4 == 0:
            raise ValueError("Ошибка безопасности не верный length payload")
        if not message.msg_id % 2 != 0:
            raise ValueError("Ошибка безопасности не верный msg_id")

        return message

    def disconnect(self):
        try:
            self.sock.close()
        except:
            pass
        self._state = 0

    async def connect(self, address=("149.154.167.51", 443), socket_timeout=10, retrying=3):
        if self._state != 0:
            return self.client.info("Клиент уже подключён")

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.settimeout(socket_timeout)
        self.sock.setblocking(False)

        for _ in range(retrying):
            try:
                await self.loop.sock_connect(self.sock, address)
                await self.loop.sock_sendall(self.sock, b"\xef")
            except BaseException as ex:
                self.client.error(f"Ошибка подключения -> {ex}")
                await asyncio.sleep(1.5)
            else:
                self.client.info(f"Подключено к {address}")
                self._state = 1
                return
        self.client.error(f"Не подключился к {address}, попыток - {retrying}")
        raise ConnectionError()

    async def send(self, data):
        length = len(data) // 4

        try:
            if length < 127:
                data = bytes([length]) + data
            else:
                data = length.to_bytes(3, "little") + data
            await self.loop.sock_sendall(self.sock, data)
        except BaseException as ex:
            self.client.error(f"Ошибка отправки -> {ex}")

    async def recv(self):
        length = await self.loop.sock_recv(self.sock, 1)

        if not length:
            return None
        if length == b"\x7f":
            length = await self.loop.sock_recv(self.sock, 3)
            if not length:
                return None
            length = struct.unpack("<I", length + b"\x00")[0] * 4
        else:
            length = length[0] * 4

        data = bytearray(length)

        try:
            lbytes = await asyncio.wait_for(self.loop.sock_recv_into(self.sock, data), timeout=10)
        except (OSError, asyncio.TimeoutError):
            return None
        if lbytes == length:
            return data
        if lbytes == 0:
            return None

        view = memoryview(data)

        while lbytes < length:
            try:
                chunk_size = await asyncio.wait_for(self.loop.sock_recv_into(self.sock, view[lbytes:]), timeout=10)
            except (OSError, asyncio.TimeoutError):
                return None
            if chunk_size == 0:
                return None
            lbytes += chunk_size
        return data


class Session:
    def __init__(self, client, loop, mt_workers=2):
        self.client = client
        self.loop = loop

        self.msg_factory = MsgFactory(self)
        self.connection = Connect(self.client, self.loop)
        self.pool_executor = ThreadPoolExecutor(max_workers=mt_workers)

        self._state = 0
        self._state_workers = [asyncio.Event(), asyncio.Event()]
        self._start_config = {}

        self.ignore_error = 0
        self.wait_packet = {}
        self.time_offset = None
        self.pending_acks = set()
        self.recent_msg_ids  = set()

    def server_time(self):
        return time.time() + (self.time_offset or 0)

    async def handle_message(self, msg):
        if msg.seq_no % 2 != 0:
            if msg.msg_id in self.pending_acks:
                return
            else:
                self.pending_acks.add(msg.msg_id)

        if self.ignore_error > 10:
            return await self.stop()

        time_diff = msg.msg_id - self.msg_factory.get_msg_id()

        if time_diff > 128849018880:
            self.client.error("Ошибка времени, разница во времени 30 секунд")
            self.ignore_error += 1
            return
        if time_diff < -1288490188800:
            self.client.error("Ошибка времени, разница во времени -5 минут")
            self.ignore_error += 1
            return
        if msg.msg_id in self.recent_msg_ids:
            self.client.error("Ошибка дубликата, msg_id уже существует!")
            self.ignore_error += 1
            return

        if msg.body["_"] == "newSessionCreated":
            self.client.info("NewSessionCreated")
            return

        msg_id = None

        if msg.body["_"] in {"rpcResult", "futureSalts"}:
            msg_id = msg.body["req_msg_id"]
        elif msg.body["_"] == "pong":
            msg_id = msg.body["msg_id"]
        elif msg.body["_"] in {"badMsgNotification", "badServerSalt"}:
            msg_id = msg.body["bad_msg_id"]
        else:
            self.loop.create_task(self.client.handle_updates(msg.body))

        if msg_id in self.wait_packet:
            self.wait_packet[msg_id].value = msg.body
            self.wait_packet[msg_id].set()

    async def handle_packet(self, packet):
        try:
            data = await self.loop.run_in_executor(
                self.pool_executor,
                self.connection.unpack,
                packet
            )
        except BaseException as ex:
            self.client.error(ex)
            return await self.stop()

        new_offset = (data.msg_id >> 32) - time.time()
        if self.time_offset is None or abs(new_offset - self.time_offset) > 5:
            self.time_offset = new_offset

        if data.body["_"] == "msgContainer":
            for msg in data.body["messages"]:
                self.loop.create_task(self.handle_message(msg))
        else:
            self.loop.create_task(self.handle_message(data))

        if len(self.pending_acks) > 10:
            await self.send({
                "_": "msgsAck",
                "msg_ids": list(self.pending_acks)
            }, False)
            self.pending_acks.clear()

    async def recv_worker(self):
        while self._state in {1, 2}:
            packet = await self.connection.recv()

            if packet is None:
                self.client.error("Сервер ничего не отправил")
                break
            if len(packet) == 4:
                if packet == b"l\xfe\xff\xff":
                    self.client.error("Ошибка 404 (AuthKeyNotFound) указанный идентификатор ключ не может быть найден DC / какой-либо из указанных запросов неправильный / некоторые поля MTProto неверны")
                elif packet == b"S\xfe\xff\xff":
                    self.client.error("Ошибка 429 (TransportFlood) слишком много транспортных соединений с одним IP / какой-либо из ограничений контейнера (сервисного сообщения) достигнут")
                elif packet == b"D\xfe\xff\xff":
                    self.client.error("Ошибка 444 (InvalidDC) возвращается при создании ключей, подключающегося к MTProxy если указан неверный DC ID")
                else:
                    self.client.error(f"Неизвестная ошибка сервера - {struct.unpack('<i', packet)[0]}")
                break

            self.loop.create_task(self.handle_packet(packet))

        self._state_workers[0].set()
        await self.stop()

    async def ping_worker(self):
        while self._state == 2:
            await asyncio.sleep(20)
            try:
                await self.send({
                    "_": "pingDelayDisconnect",
                    "ping_id": self.msg_factory.get_msg_id(),
                    "disconnect_delay": 25
                }, False)
            except:
                break

        self._state_workers[1].set()
        await self.stop()

    async def send(self, body: dict, response=True, timeout=10):
        # print("send", body) # DEBUG LOG
        message = self.msg_factory.create(body)

        if response:
            self.wait_packet[message.msg_id] = asyncio.Event()
            self.wait_packet[message.msg_id].value = None

        data = await self.loop.run_in_executor(
            self.pool_executor,
            self.connection.pack,
            message
        )

        try:
            await self.connection.send(data)
        except BaseException as ex:
            self.wait_packet.pop(message.msg_id, None)
            raise ex

        if not response:
            return

        try:
            await asyncio.wait_for(self.wait_packet[message.msg_id].wait(), timeout)
        except asyncio.TimeoutError:
            pass

        result = self.wait_packet.pop(message.msg_id).value

        # print("send result", result) # DEBUG LOG

        if result is None:
            raise TimeoutError("Время запроса вышло")
        elif result["_"] == "rpcError":
            raise Exception(f"RpcError [{result['error_code']}] - {result['error_message']} (by {body['_']})")
        elif result["_"] == "badMsgNotification":
            if result.error_code in BADMSGNOTIFICATIONS:
                self.client.warn(f"BadMsgNotification [{result['error_code']}] - {BADMSGNOTIFICATIONS[result['error_code']]}")
            else:
                self.client.warn(f"BadMsgNotification [{result['error_code']}] - Неизвестный код ошибки")
        elif result["_"] == "badServerSalt":
            self.connection.salt = result["new_server_salt"]
            return await self.send(body, response, timeout)

        return result

    async def invoke(self, query, timeout=15, retrying=5, retry_delay=1.5):
        try:
            data = await self.send(query, timeout=timeout)
            if not data:
                return None
            return data["result"]
        except Exception as ex:
            self.client.warn(f"Ошибка отправки invoke -> {ex}")
            await asyncio.sleep(retry_delay) # TODO добавить обработку FloodWait, FloodPremiumWait

        for _ in range(retrying):
            try:
                data = await self.send(query, timeout=timeout)
                if not data:
                    return None
                return data["result"]
            except Exception as ex:
                self.client.warn(f"Ошибка отправки invoke -> {ex}")
                await asyncio.sleep(retry_delay)

        raise TimeoutError(f"Ошибка отправки invoke, исчерпаны попытки({retrying}) -> {query}")

    async def stop(self):
        if self._state != 2:
            return self.client.warn(f"Статус сессии == {self._state}, остановка пропущена")

        self._state = 3

        await asyncio.wait_for(self._state_workers[0].wait(), timeout=None)
        await asyncio.wait_for(self._state_workers[1].wait(), timeout=None)

        self._state_workers[0].clear()
        self._state_workers[1].clear()

        self.connection.disconnect()

        self._state = 0

        await self.start()

    async def start(self, device_model="Ncore python", system_version="10.0", app_version="4.0", system_lang_code="ru", lang_pack="tdesktop", lang_code="ru"):
        if self._state != 0:
            return self.client.warn(f"Статус сессии == {self._state}, запуск пропущен")

        if not self._start_config:
            self._start_config = {
                "device_model": device_model,
                "system_version": system_version,
                "app_version": app_version,
                "system_lang_code": system_lang_code,
                "lang_pack": lang_pack,
                "lang_code": lang_code,
            }

        try:
            self._state = 1
            await self.connection.connect()
            self.loop.create_task(self.recv_worker())
            await self.send({"_": "ping", "ping_id": 0}, timeout=5)
            await self.send({
                "_": "invokeWithLayer",
                "layer": 214,
                "query": {
                    "_": "initConnection",
                    "api_id": self.client.api_id,
                    **self._start_config,
                    "query": {
                        "_": "getConfig"
                    }
                }
            }, timeout=5)

            if self.connection._isAuth == 1:
                botauth = await self.invoke({
                    "_": "auth.importBotAuthorization",
                    "flags": 0,
                    "api_id": self.client.api_id,
                    "api_hash": self.client.api_hash,
                    "bot_auth_token": self.client.bot_token,
                })

                self.client.storage["id"] = botauth["user"]["id"]
                self.client.storage["first_name"] = botauth["user"]["first_name"]
                self.client.storage["username"] = botauth["user"]["username"]
                self.client.save_storage()

            self._state = 2
            self.loop.create_task(self.ping_worker())
        except Exception as ex:
            self._state = 0
            self.client.error(f"Ошибка запуска сессии -> {ex}")