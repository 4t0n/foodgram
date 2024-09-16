import base64
import random
import string

from django.contrib.auth import get_user_model
from django.core.exceptions import SuspiciousOperation
from django.core.files.base import ContentFile
from django.db import IntegrityError
from djoser.serializers import UserSerializer, UserCreateSerializer
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from foodgram_backend.constants import SHORT_LINK_LENGTH
from recipes.models import Ingredient, Recipe, RecipeIngredient, Tag
from users.models import Follow

User = get_user_model()


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]

            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return super().to_internal_value(data)


class CustomUserSerializer(UserSerializer):
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
        if request and request.user.is_authenticated:
            return request.user in obj.followers.all()
        return False


class CustomUserCreateSerializer(UserCreateSerializer):
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
    author = CustomUserSerializer(read_only=True)
    tags = TagSerializer(many=True)
    ingredients = IngredientDetailSerializer(
        many=True,
        source='recipe_to_ingredient',
    )

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
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

    def create(self, validated_data: dict):
        ingredients_data = validated_data.pop('ingredients')
        instance = super().create(validated_data)
        short_link = ''.join(
            random.choices(
                string.ascii_letters + string.digits,
                k=SHORT_LINK_LENGTH
            )
        )
        while True:
            try:
                instance.short_link = short_link
                instance.save()
                break
            except IntegrityError:
                pass
        RecipeIngredient.objects.bulk_create([
            RecipeIngredient(
                recipe=instance,
                ingredient=ingredient['id'],
                amount=ingredient['amount']
            ) for ingredient in ingredients_data
        ])
        return instance

    def update(self, instance, validated_data):
        ingredients_data = validated_data.get('ingredients')
        tags_data = validated_data.get('tags')
        instance.ingredients.clear()
        RecipeIngredient.objects.filter(recipe=instance).delete()
        RecipeIngredient.objects.bulk_create([
            RecipeIngredient(
                recipe=instance,
                ingredient=ingredient['id'],
                amount=ingredient['amount']
            ) for ingredient in ingredients_data
        ])
        instance.tags.clear()
        instance.tags.set(tags_data)
        instance.image = validated_data.get('image', instance.image)
        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get(
            'cooking_time', instance.cooking_time)
        instance.save()
        return instance

    def get_fields(self, *args, **kwargs):
        fields = super().get_fields(*args, **kwargs)
        request = self.context.get('request', None)
        if request and getattr(request, 'method', None) == "PATCH":
            fields['image'].required = False
        return fields

    def to_representation(self, instance):
        serializer = RecipeSerializer(instance)
        return serializer.data


class GetLinkSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = ('short_link',)
        read_only_fields = ('short_link',)


class FollowSerializer(CustomUserSerializer):
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    def get_recipes(self, obj):
        serializer = RecipeBaseSerializer(obj.user_recipes.all(), many=True)
        return serializer.data

    def get_recipes_count(self, obj):
        serializer = RecipeBaseSerializer(obj.user_recipes.all(), many=True)
        return len(serializer.data)

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


class SubscribeSerializer(FollowSerializer):

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
        read_only_fields = (
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
