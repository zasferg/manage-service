from typing import List, Tuple
import re


class PasswordValidator:

    @classmethod
    def validate_password(
        cls,
        password: str,
        min_length: int = 8,
        require_digits: bool = True,
        require_uppercase: bool = True,
        require_lowercase: bool = True,
        require_special: bool = True,
    ) -> Tuple[bool, List[str]]:

        errors = []

        if len(password) < min_length:
            errors.append(f"Пароль должен содержать минимум {min_length} символов")
        if require_digits and not re.search(r"\d", password):
            errors.append("Пароль должен содержать хотя бы одну цифру")
        if require_uppercase and not re.search(r"[A-Z]", password):
            errors.append("Пароль должен содержать хотя бы одну заглавную букву")
        if require_lowercase and not re.search(r"[a-z]", password):
            errors.append("Пароль должен содержать хотя бы одну строчную букву")
        if require_special and not re.search(
            r'[!@#$%^&*()_+\-=\[\]{};\':"\\|,.<>/?]', password
        ):
            errors.append("Пароль должен содержать хотя бы один специальный символ")

        return len(errors) == 0, errors

    @classmethod
    def validate_and_raise(cls, password: str, **kwargs) -> str:

        is_valid, errors = cls.validate_password(password, **kwargs)
        if not is_valid:
            raise ValueError("; ".join(errors))
        return password
