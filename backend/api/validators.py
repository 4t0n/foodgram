from rest_framework.validators import ValidationError

from foodgram_backend.constants import MAX_RECIPES_LIMIT


def validate_recipes_limit(value):
    try:
        recipes_limit = int(value)
        if recipes_limit < 0 or recipes_limit > MAX_RECIPES_LIMIT:
            raise ValidationError
    except (TypeError, ValueError, ValidationError):
        raise ValidationError
