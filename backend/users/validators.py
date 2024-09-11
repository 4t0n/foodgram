from django.core.exceptions import ValidationError


def name_validator(value):
    if value == 'me':
        raise ValidationError(
            'Использовать "me", в качестве username-запрещено!')
    return value
