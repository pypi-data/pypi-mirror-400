class KundolukError(Exception):
    """Базовое исключение для всей библиотеки"""
    pass

class APIError(KundolukError):
    """Ошибки, прилетевшие от сервера (4xx, 5xx)"""
    def __init__(self, message: str, status_code: int):
        self.status_code = status_code
        self.message = message
        super().__init__(f"Ошибка API ({status_code}): {message}")

class ValidationError(APIError):
    """Ошибки валидации (неверный пароль или логин)"""
    def __init__(self, message: str, status_code: int = 400):
        super().__init__(status_code, message)

class AuthError(APIError):
    """Токен умер или его нет"""
    def __init__(self, message: str = "Сессия истекла или его не существует", status_code: int = 401):
        super().__init__(status_code, message)