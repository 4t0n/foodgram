from django_filters import BooleanFilter, FilterSet


class RecipeFilter(FilterSet):
    is_favorited = BooleanFilter(field_name='is_favorite')

