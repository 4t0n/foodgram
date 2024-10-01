from django.contrib.auth import get_user_model
from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator, ValidationError

from recipes.models import Ingredient, Recipe, RecipeIngredient, Tag
from users.models import Favorite, Follow, ShoppingCart

from .utils import Base64ImageField
from .validators import validate_recipes_limit

User = get_user_model()


class FoodgramUserSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField(
        read_only=True,
        default=False,
    )

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'avatar',
        )

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        return (
            request
            and request.user.is_authenticated
            and obj.followers.filter(id=request.user.id).exists()
        )


class FoodgramUserCreateSerializer(UserCreateSerializer):
    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'password',
        )
        read_only_fields = ('id',)


class AvatarSerializers(serializers.ModelSerializer):
    avatar = Base64ImageField(required=True, allow_null=True)

    class Meta:
        model = User
        fields = ('avatar',)


class FollowSerializer(FoodgramUserSerializer):
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'recipes',
            'recipes_count',
            'is_subscribed',
            'avatar',
        )

    def get_recipes(self, obj):
        recipes_limit = self.context.get('request').query_params.get(
            'recipes_limit'
        )
        query = obj.user_recipes.all()
        if recipes_limit:
            try:
                validate_recipes_limit(recipes_limit)
                query = obj.user_recipes.all()[: int(recipes_limit)]
            except ValidationError:
                pass
        serializer = RecipeBaseSerializer(
            query,
            many=True,
        )
        return serializer.data

    def get_recipes_count(self, obj):
        return obj.user_recipes.count()


class CreateSubscribeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Follow
        fields = (
            'user',
            'author',
        )
        validators = [
            UniqueTogetherValidator(
                queryset=Follow.objects.all(),
                fields=('user', 'author'),
                message='Вы уже подписаны на этого пользователя!',
            )
        ]

    def validate_author(self, author):
        if author == self.context['request'].user:
            raise ValidationError('Нельзя подписаться на самого себя!')
        return author

    def to_representation(self, instance):
        serializer = FollowSerializer(
            instance.author,
            context={'request': self.context.get('request')},
        )
        return serializer.data


class CreateFavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favorite
        fields = (
            'user',
            'recipe',
        )
        validators = [
            UniqueTogetherValidator(
                queryset=Favorite.objects.all(),
                fields=('user', 'recipe'),
                message='Рецепт уже добавлен в избранное!',
            )
        ]

    def to_representation(self, instance):
        serializer = RecipeBaseSerializer(
            instance.recipe,
            context={'request': self.context.get('request')},
        )
        return serializer.data


class CreateShoppingSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShoppingCart
        fields = (
            'user',
            'recipe',
        )
        validators = [
            UniqueTogetherValidator(
                queryset=ShoppingCart.objects.all(),
                fields=('user', 'recipe'),
                message='Рецепт уже добавлен в корзину!',
            )
        ]

    def to_representation(self, instance):
        serializer = RecipeBaseSerializer(
            instance.recipe,
            context={'request': self.context.get('request')},
        )
        return serializer.data


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class IngredientDetailSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(
        source='ingredient.id',
    )
    name = serializers.ReadOnlyField(
        source='ingredient.name',
    )
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit',
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class IngredientCreateSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(),
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')


class RecipeBaseSerializer(serializers.ModelSerializer):
    image = Base64ImageField(required=True, allow_null=True)

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time',
        )


class RecipeSerializer(RecipeBaseSerializer):
    author = FoodgramUserSerializer(read_only=True)
    tags = TagSerializer(many=True)
    ingredients = IngredientDetailSerializer(
        many=True,
        source='recipe_to_ingredient',
    )
    is_favorited = serializers.BooleanField(read_only=True)
    is_in_shopping_cart = serializers.BooleanField(read_only=True)

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',
        )


class RecipeCreateSerializer(serializers.ModelSerializer):
    ingredients = IngredientCreateSerializer(many=True)
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'ingredients',
            'tags',
            'image',
            'name',
            'text',
            'cooking_time',
        )

    def validate(self, attrs):
        if not attrs.get('ingredients'):
            raise serializers.ValidationError(
                {'ingredients': 'Отсутствуют ингредиенты!'}
            )
        if not attrs.get('tags'):
            raise serializers.ValidationError({'tags': 'Отсутствуют теги!'})
        return super().validate(attrs)

    def validate_ingredients(self, ingredients):
        if not ingredients:
            raise serializers.ValidationError(
                {'ingredients': 'Отсутствуют ингредиенты!'}
            )
        if len(ingredients) != len(set(ing['id'] for ing in ingredients)):
            raise serializers.ValidationError(
                {'ingredients': 'Ингредиенты повторяются!'}
            )
        return ingredients

    def validate_tags(self, tags):
        if not tags:
            raise serializers.ValidationError({'tags': 'Отсутствуют теги!'})
        if len(tags) != len(set(tags)):
            raise serializers.ValidationError({'tags': 'Теги повторяются!'})
        return tags

    def recipe_ingredient_create(self, instance, ingredients_data):
        RecipeIngredient.objects.bulk_create(
            [
                RecipeIngredient(
                    recipe=instance,
                    ingredient=ingredient['id'],
                    amount=ingredient['amount'],
                )
                for ingredient in ingredients_data
            ]
        )

    def create(self, validated_data: dict):
        ingredients_data = validated_data.pop('ingredients')
        instance = super().create(validated_data)
        instance.save()
        self.recipe_ingredient_create(instance, ingredients_data)
        return instance

    def update(self, instance, validated_data):
        ingredients_data = validated_data.get('ingredients')
        tags_data = validated_data.get('tags')
        instance.ingredients.clear()
        instance.tags.clear()
        instance.tags.set(tags_data)
        RecipeIngredient.objects.filter(recipe=instance).delete()
        self.recipe_ingredient_create(instance, ingredients_data)
        instance.image = validated_data.get('image', instance.image)
        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get(
            'cooking_time', instance.cooking_time
        )
        instance.save()
        return instance

    def get_fields(self, *args, **kwargs):
        fields = super().get_fields(*args, **kwargs)
        request = self.context.get('request', None)
        if request and getattr(request, 'method', None) == "PATCH":
            fields['image'].required = False
        return fields

    def to_representation(self, instance):
        serializer = RecipeSerializer(
            Recipe.objects.annotated_fields(
                self.context.get('request').user
            ).get(pk=instance.pk),
            context=self.context,
        )
        return serializer.data


class GetLinkSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = ('short_link',)
