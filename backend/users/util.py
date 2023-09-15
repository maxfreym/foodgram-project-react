from django.conf import settings
from django.core.exceptions import ValidationError


def username_validator(username):
    if username.lower() in settings.STOP_WORD:
        raise ValidationError(
            'имя пользователя находится в списке запрещенных')
