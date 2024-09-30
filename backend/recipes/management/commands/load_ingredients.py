import json

from django.core.management.base import BaseCommand
from django.db.utils import IntegrityError

from recipes.models import Ingredient


class Command(BaseCommand):
    def handle(self, *args, **options):
        fail_count = 0
        success_count = 0
        with open('recipes/management/commands/ingredients.json', 'rb') as f:
            data = json.load(f)
            for obj in data:
                ingredient = Ingredient()
                ingredient.name = obj['name']
                ingredient.measurement_unit = obj['measurement_unit']
                try:
                    ingredient.save()
                    success_count += 1
                except IntegrityError:
                    fail_count += 1
                    continue
            print(
                f'Загружено {success_count} ингредиентов в БД. '
                f'{fail_count} ингредиентов не удалось загрузить.'
            )
