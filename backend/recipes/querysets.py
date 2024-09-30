from django.db import models
from django.db.models import ExpressionWrapper, Q, Value


class RecipeQuerySet(models.QuerySet):
    def annotated_fields(self, user):
        from .models import Recipe

        if user.is_authenticated:
            return (
                self.select_related('author')
                .prefetch_related('tags', 'ingredients')
                .annotate(
                    is_favorited=ExpressionWrapper(
                        Q(
                            id__in=Recipe.objects.filter(favorite=user).values(
                                'id'
                            )
                        ),
                        output_field=models.BooleanField(),
                    ),
                    is_in_shopping_cart=ExpressionWrapper(
                        Q(
                            id__in=Recipe.objects.filter(shopping=user).values(
                                'id'
                            )
                        ),
                        output_field=models.BooleanField(),
                    ),
                )
            )
        return self.annotate(
            is_favorited=Value(False), is_in_shopping_cart=Value(False)
        )
