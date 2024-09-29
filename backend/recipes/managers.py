from django.db import models


class RecipeManager(models.Manager):
    def is_favorited(self, user, recipe):
        recipes = self.filter(favorite=user)
        return recipe in recipes
