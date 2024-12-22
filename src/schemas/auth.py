from datetime import datetime
from uuid import UUID

import jwt
from pydantic import BaseModel, Field


class ProtoJWT(BaseModel):
    """
    Модель прототипа JWT токенов
    """

    jti: UUID = Field(..., description="UUID токена")
    user_id: UUID = Field(..., description="UUID пользователя")
    iat: float = Field(
        ..., description="Время создания токена в формате epoch"
    )
    exp: float = Field(
        ..., description="Время истечения токена в формате epoch"
    )
    role: str = Field(..., description="Связанная роль")

    @property
    def issued_at(self) -> datetime:
        return datetime.fromtimestamp(self.iat)

    @property
    def expires_at(self) -> datetime:
        return datetime.fromtimestamp(self.exp)

    @classmethod
    def from_jwt(
            cls,
            token: str,
            secret_key: str | None
    ):
        """
        Создает экземпляр ProtoJWT из JWT токена.

        :param token: JWT токен в виде строки.
        :param secret_key: Секретный ключ для декодирования токена.
        :return: Экземпляр ProtoJWT.
        """
        if secret_key is None:
            payload = jwt.decode(
                token,
                options={"verify_signature": False}
            )
            return cls(**payload)
        else:
            raise NotImplementedError


class AccessJWT(ProtoJWT):
    pass


class RefreshJWT(ProtoJWT):
    pass
