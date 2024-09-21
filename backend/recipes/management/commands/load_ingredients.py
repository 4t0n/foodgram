import json

from django.core.management.base import BaseCommand
from django.db.utils import IntegrityError

from recipes.models import Ingredient


class Command(BaseCommand):
    def handle(self, *args, **options):

        with open('recipes/management/commands/ingredients.json', 'rb') as f:
            data = json.load(f)
            for obj in data:
                ingredient = Ingredient()
                ingredient.name = obj['name']
                ingredient.measurement_unit = obj['measurement_unit']
                try:
                    ingredient.save()
                except IntegrityError:
                    continue
