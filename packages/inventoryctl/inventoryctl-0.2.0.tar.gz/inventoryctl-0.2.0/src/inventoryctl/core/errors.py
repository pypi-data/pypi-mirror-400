from enum import Enum

class ExitCode(int, Enum):
    SUCCESS = 0
    USER_ERROR = 1
    VALIDATION_ERROR = 2
    CONFLICT = 3
    INTERNAL_ERROR = 4

class InventoryError(Exception):
    def __init__(self, message: str, exit_code: ExitCode = ExitCode.INTERNAL_ERROR):
        self.message = message
        self.exit_code = exit_code
        super().__init__(message)

class UserError(InventoryError):
    def __init__(self, message: str):
        super().__init__(message, ExitCode.USER_ERROR)

class ValidationError(InventoryError):
    def __init__(self, message: str):
        super().__init__(message, ExitCode.VALIDATION_ERROR)

class ConflictError(InventoryError):
    def __init__(self, message: str):
        super().__init__(message, ExitCode.CONFLICT)
