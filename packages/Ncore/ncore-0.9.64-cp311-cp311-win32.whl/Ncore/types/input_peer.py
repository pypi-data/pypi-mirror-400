from typing import overload


class InputPeerEmpty:
    def __new__(cls) -> dict:
        return {"_": "inputPeerEmpty"}


class InputPeerSelf:
    def __new__(cls) -> dict:
        return {"_": "inputPeerSelf"}


class InputPeerChat:
    @overload
    def __new__(cls, chat_id: int) -> dict:
        ...

    def __new__(cls, chat_id: int):
        return {"_": "inputPeerChat", "chat_id": chat_id}


class InputPeerUser:
    @overload
    def __new__(cls, user_id: int, access_hash: int) -> dict:
        ...

    def __new__(cls, user_id: int, access_hash: int):
        return {"_": "inputPeerUser", "user_id": user_id, "access_hash": access_hash}


class InputPeerChannel:
    @overload
    def __new__(cls, user_id: int, access_hash: int) -> dict:
        ...

    def __new__(cls, user_id: int, access_hash: int):
        return {"_": "inputPeerChannel", "user_id": user_id, "access_hash": access_hash}