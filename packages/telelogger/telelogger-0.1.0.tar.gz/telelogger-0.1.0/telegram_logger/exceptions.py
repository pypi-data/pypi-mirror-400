"""
Исключения для Telegram API
Иерархия ошибок от общих к конкретным
"""


class TelegramError(Exception):
    """
    Базовый класс для всех ошибок, связанных с Telegram API.

    Этот класс расширяет стандартное исключение Exception,
    добавляя возможность хранить оригинальное сообщение об ошибке от Telegram API.

    Attributes:
        api_error (str | None): Оригинальное сообщение об ошибке,
                                полученное от Telegram API.
                                None, если ошибка не от API (например, сетевые проблемы).
    """

    def __init__(self, message: str, api_error: str = None):
        """
        Инициализирует исключение TelegramError.

        Args:
            message (str): Понятное сообщение об ошибке на русском языке,
                          предназначенное для пользователя.
                          Пример: "Не удалось отправить сообщение"

            api_error (str, optional): Оригинальное сообщение об ошибке от Telegram API.
                                      Пример: "Forbidden: bot was blocked by the user"
                                      Если None, считается что ошибка не от API.
        """

        # Сохраняем оригинальную ошибку от Telegram API в атрибуте объекта.
        # Это позволяет получить доступ к оригинальному сообщению позже,
        # например для логирования или детального анализа ошибки.
        # Доступ: error.api_error
        self.api_error = api_error

        # Создаем полное сообщение для пользователя.
        # Начинаем с основного сообщения (message).
        full_message = message

        # Если есть оригинальное сообщение от Telegram API (api_error),
        # добавляем его в скобках для большей информативности.
        # Пример: "Не удалось отправить сообщение (Telegram: Forbidden: bot was blocked)"
        if api_error:
            full_message = f"{message} (Telegram: {api_error})"

        # Вызываем конструктор родительского класса Exception,
        # передавая ему сформированное полное сообщение.
        # Это сообщение будет доступно стандартными способами:
        # - str(error) вернет full_message
        # - error.args[0] также содержит full_message
        super().__init__(full_message)


# Группа 1: Ошибки токена
class TokenError(TelegramError):
    """Общая ошибка токена"""
    pass

class TokenFormatError(TokenError):
    """Неверный формат токена (синхронная проверка)"""
    pass

class TokenInvalidError(TokenError):
    """Токен невалиден (ошибка от Telegram API)"""
    pass

class TokenRevokedError(TokenError):
    """Токен был отозван/удален"""
    pass


# Группа 2: Ошибки чата
class ChatError(TelegramError):
    """Общая ошибка чата"""
    pass

class ChatNotFoundError(ChatError):
    """Чат не найден (не существует или неправильный ID)"""
    pass

class ChatAccessError(ChatError):
    """Нет доступа к чату"""
    pass

class BotBlockedError(ChatAccessError):
    """Бот заблокирован пользователем"""
    pass

class BotKickedError(ChatAccessError):
    """Бота выгнали из группы/канала"""
    pass

class InsufficientPermissionsError(ChatAccessError):
    """Недостаточно прав (например, нет прав писать в канал)"""
    pass


# Группа 3: Сетевые ошибки
class NetworkError(TelegramError):
    """Проблемы с сетью или соединением"""
    pass

class TimeoutError(NetworkError):
    """Таймаут запроса"""
    pass


# Группа 4: Другие ошибки
class BotAlreadyExistsError(TelegramError):
    """Бот с таким токеном уже используется"""
    pass