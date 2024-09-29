from rest_framework.validators import ValidationError

from foodgram_backend.constants import MAX_RECIPES_LIMIT


def validate_recipes_limit(value):
    """Проверка фильтра recipes_limit."""
    try:
        recipes_limit = int(value)
    except ValueError:
        raise ValidationError
    if recipes_limit < 0 or recipes_limit > MAX_RECIPES_LIMIT:
        raise ValidationError
