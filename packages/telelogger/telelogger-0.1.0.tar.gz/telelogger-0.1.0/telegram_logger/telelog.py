import re
import weakref
import logging
from typing import Optional, List, Dict, Any
import requests

# Предполагается, что эти исключения определены в telegram_logger.exceptions
from telegram_logger.exceptions import (
    BotAlreadyExistsError,
    TokenFormatError,
    TokenInvalidError,
    TokenRevokedError,
    TokenError,
    NetworkError,
    InsufficientPermissionsError,
    ChatNotFoundError,
    BotBlockedError,
    BotKickedError,
    ChatAccessError,
    ChatError,
    TelegramError,
)

API_URL = "https://api.telegram.org"
DEFAULT_TIMEOUT = 5
SEND_TIMEOUT = 10
MAX_MESSAGE_LENGTH = 4096
_TOKEN_RE = re.compile(r"^\d{9,11}:[A-Za-z0-9_-]{35}$")


class TelegramLogHandler:
    """
    Утилитный класс для отправки логов в Telegram-чат через бота.
    Гарантирует уникальность экземпляра на токен (WeakValueDictionary).
    """
    _instances: "weakref.WeakValueDictionary[str, TelegramLogHandler]" = weakref.WeakValueDictionary()

    def __new__(cls, token: str, chat_id: int):
        if token in cls._instances:
            raise BotAlreadyExistsError("Бот с таким токеном уже существует")
        return super().__new__(cls)

    def __init__(self, token: str, chat_id: int, *, session: Optional[requests.Session] = None):
        """
        Инициализация: проверка формата токена, валидность токена и доступ к чату.
        """
        try:
            if not self._validate_token_format(token):
                raise TokenFormatError("Неверный формат токена")

            self.token = token
            self.chat_id = chat_id
            self._session = session or requests.Session()

            # Проверяем токен и чат через API
            self._validate_token()
            self._validate_chat_id()

            # Регистрируем экземпляр
            self.__class__._instances[token] = self

        except (TokenError, ChatError, NetworkError, BotAlreadyExistsError):
            raise
        except Exception as e:
            raise TelegramError(f"Неожиданная ошибка при инициализации: {e}")

    # --- Служебные методы и HTTP-обёртка ---

    def _api_request(self, http_method: str, endpoint: str, *, json: Optional[Dict[str, Any]] = None,
                     params: Optional[Dict[str, Any]] = None, timeout: Optional[int] = None) -> Dict[str, Any]:
        """
        Универсальная обёртка для запросов к Telegram API.
        Возвращает распарсенный JSON (словарь) и бросает наши исключения при ошибках сети.
        """
        url = f"{API_URL}/bot{self.token}/{endpoint}"
        timeout = timeout or DEFAULT_TIMEOUT

        try:
            if http_method.lower() == "get":
                resp = self._session.get(url, params=params, timeout=timeout)
            elif http_method.lower() == "post":
                resp = self._session.post(url, json=json, params=params, timeout=timeout)
            else:
                raise ValueError("Unsupported HTTP method: " + http_method)

            # Пытаемся распарсить JSON (Telegram всегда возвращает JSON)
            data = resp.json() if resp.content else {}

            return {"status_code": resp.status_code, "data": data}

        except requests.exceptions.Timeout:
            raise TimeoutError("Таймаут при обращении к серверу Telegram")
        except requests.exceptions.ConnectionError:
            raise NetworkError("Нет соединения с сервером Telegram")
        except requests.exceptions.RequestException as e:
            raise NetworkError(f"Сетевая ошибка при обращении к Telegram: {e}")

    # --- Валидации ---

    def _validate_token_format(self, token: str) -> bool:
        return bool(token and _TOKEN_RE.match(token))

    def _validate_token(self) -> bool:
        """Проверяем токен методом getMe."""
        result = self._api_request("get", "getMe")
        status = result["status_code"]
        data = result["data"]

        if status == 200 and data.get("ok"):
            return True

        description = (data.get("description") or "Unknown error").lower()

        if status == 401:
            raise TokenInvalidError("Неверный токен бота", api_error=description)
        if status == 404:
            raise TokenRevokedError("Токен был удален или отозван", api_error=description)
        if status == 429:
            raise TokenError("Слишком много запросов. Попробуйте позже", api_error=description)

        raise TokenError(f"Ошибка проверки токена (HTTP {status})", api_error=description)

    def _validate_chat_id(self) -> bool:
        """Проверяем доступность чата и базовые права."""
        payload = {"chat_id": str(self.chat_id)}
        result = self._api_request("post", "getChat", json=payload)
        status = result["status_code"]
        data = result["data"]

        if status == 200 and data.get("ok"):
            chat_info = data["result"]
            if not self._check_chat_permissions(chat_info):
                raise InsufficientPermissionsError("Бот не имеет прав отправлять сообщения в этот чат")
            return True

        description = (data.get("description") or "").lower()

        if "chat not found" in description:
            raise ChatNotFoundError(f"Чат с ID {self.chat_id} не найден", api_error=description)
        if "bot was blocked" in description:
            raise BotBlockedError("Бот заблокирован в этом чате", api_error=description)
        if "bot was kicked" in description:
            raise BotKickedError("Бот был исключен из этого чата", api_error=description)
        if "not enough rights" in description or "insufficient rights" in description:
            raise InsufficientPermissionsError("Недостаточно прав для доступа к чату", api_error=description)

        raise ChatAccessError(f"Ошибка доступа к чату (HTTP {status})", api_error=description)

    def _check_chat_permissions(self, chat_info: Dict[str, Any]) -> bool:
        """Проверяет тип чата и коррелирующие разрешения."""
        chat_type = chat_info.get("type")
        if chat_type == "channel":
            permissions = chat_info.get("permissions", {})
            return permissions.get("can_post_messages", False)
        return True

    # --- Логика разбиения сообщений ---

    def _split_message(self, text: str) -> List[str]:
        """Разбивает текст на фрагменты <= MAX_MESSAGE_LENGTH, стараясь резать по переносам/пунктуации."""
        if not text:
            return [""]

        if len(text) <= MAX_MESSAGE_LENGTH:
            return [text]

        parts: List[str] = []
        remaining = text

        while remaining:
            if len(remaining) <= MAX_MESSAGE_LENGTH:
                parts.append(remaining)
                break

            # Ищем максимально правый разделитель в пределах лимита
            window = remaining[:MAX_MESSAGE_LENGTH]
            split_idx = None

            for sep in ("\n", ". ", "! ", "? ", "; ", ", ", " "):
                idx = window.rfind(sep)
                if idx != -1:
                    split_idx = idx + len(sep)
                    break

            if split_idx is None or split_idx == 0:
                # Жёсткий срез если не нашли разделитель
                split_idx = MAX_MESSAGE_LENGTH

            parts.append(remaining[:split_idx].rstrip())
            remaining = remaining[split_idx:].lstrip()

        return parts

    # --- Отправка сообщений ---

    def _send_message(self, text: str, parse_mode: str = "HTML", disable_notification: bool = False) -> bool:
        """Отправляет (возможно разбитое) сообщение в Telegram. Возвращает True если все части отправлены успешно."""
        endpoint = "sendMessage"
        parts = self._split_message(text)
        results: List[bool] = []

        for idx, part in enumerate(parts):
            payload = {
                "chat_id": self.chat_id,
                "text": part,
                "parse_mode": parse_mode,
                "disable_notification": disable_notification,
            }
            if len(parts) > 1:
                payload["text"] = f"Часть {idx + 1}/{len(parts)}\n\n{part}"

            try:
                result = self._api_request("post", endpoint, json=payload, timeout=SEND_TIMEOUT)
                status = result["status_code"]
                data = result["data"]
                results.append(status == 200 and data.get("ok", False))
            except Exception:
                # Локально — логируем и говорим, что часть провалена
                logging.exception("Ошибка при отправке части сообщения в Telegram")
                results.append(False)

        return all(results)

    # Публичные методы под уровни логирования
    def debug(self, message: str) -> bool:
        return self._send_message(f"🔍 DEBUG\n{message}", disable_notification=True)

    def info(self, message: str) -> bool:
        return self._send_message(f"ℹ️ INFO\n{message}")

    def warning(self, message: str) -> bool:
        return self._send_message(f"⚠️ WARNING\n{message}")

    def error(self, message: str) -> bool:
        return self._send_message(f"❌ ERROR\n{message}")

    def critical(self, message: str) -> bool:
        return self._send_message(f"🔥 CRITICAL\n{message}")

    def send(self, message: str, parse_mode: str = "HTML", disable_notification: bool = False) -> bool:
        """Отправляет произвольное сообщение."""
        return self._send_message(message, parse_mode=parse_mode, disable_notification=disable_notification)

    def close(self) -> None:
        """Закрываем сессию и удаляем из реестра экземпляров."""
        try:
            token = getattr(self, "token", None)
            if token and token in self.__class__._instances:
                self.__class__._instances.pop(token, None)
            if hasattr(self, "_session"):
                self._session.close()
        except Exception:
            logging.exception("Ошибка при закрытии TelegramLogHandler")

    def __del__(self):
        # Попытка аккуратно очистить реестр и сессию
        try:
            self.close()
        except Exception:
            pass


