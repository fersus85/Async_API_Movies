import os
import time

import aiohttp
from aiohttp import ClientResponseError
from fastapi import Request, HTTPException, status
from fastapi.params import Depends

from db.cacher import get_cacher, AbstractCache
from schemas.auth import AccessJWT


async def verify_access_token(token: str, role: str) -> None:
    async with aiohttp.ClientSession() as session:
        try:
            url = f"{os.getenv('AUTH_SERVICE_URL')}/verify"
            resp = await session.post(
                url,
                headers={"Content-Type": "application/json"},
                json={
                    "access_token": token,
                    "role": role
                }
            )
            resp.raise_for_status()
        except ClientResponseError as exc:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token"
            ) from exc


class PermissionChecker:
    """
    Класс для проверки прав доступа пользователя.

    Этот класс используется как зависимость в маршрутах FastAPI для проверки,
    имеет ли текущий пользователь роль нужного уровня доступа.
    Если у пользователя недостаточно прав,
    выбрасывается исключение HTTP 403 Forbidden.
    """

    def __init__(
            self,
            required: str
    ) -> None:
        self.required = required

    async def __call__(
        self,
        request: Request,
        cacher: AbstractCache = Depends(get_cacher)
    ) -> None:
        token = request.cookies.get("access_token")
        if not token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Access token is missing"
            )

        cache_key = str(self.__class__) + ":" + token

        # чтение кеша
        is_valid = await cacher.get(cache_key)
        if is_valid is not None:
            return

        # валидация токена
        await verify_access_token(token, self.required)

        # кэширование результата на время жизни токена
        access_jwt = AccessJWT.from_jwt(token, secret_key=None)
        issue_epoch = access_jwt.exp

        diff = int(issue_epoch - time.time())
        if diff <= 0:
            return

        await cacher.set(cache_key, True, expire=diff)
