from django.contrib.auth import get_user_model
from django.db.models import F
from djoser.serializers import UserCreateSerializer, UserSerializer
from drf_base64.fields import Base64ImageField
from recipes.models import (
    FavoriteRecipe,
    Ingredient,
    IngredientInRecipe,
    Recipes,
    ShoppingCart,
    Tag,
)
from rest_framework import serializers
from rest_framework.generics import get_object_or_404
from rest_framework.validators import UniqueValidator
from users.models import CustomFollow

User = get_user_model()


class GetIsSubscribedMixin:
    """Отображение подписки"""

    def get_is_subscribed(self, obj):
        user = self.context.get("request").user
        if user.is_anonymous:
            return False
        return user.follower.filter(author=obj.id).exists()


class GetIngredientsMixin:
    """Миксин для рецептов"""

    def get_ingredients(self, obj):
        return obj.ingredients.values(
            "id",
            "name",
            "measurement_unit",
            amount=F("ingredients_amount__amount"),
        )


class CustomUserCreateSerializer(UserCreateSerializer):
    """Сериализатор для создания пользователя"""

    email = serializers.EmailField(
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    username = serializers.CharField(
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    first_name = serializers.CharField()
    last_name = serializers.CharField()

    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "username",
            "first_name",
            "last_name",
            "password",
        )


class CustomUserListSerializer(GetIsSubscribedMixin, UserSerializer):
    """Сериализатор для просмотра пользователя"""

    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "is_subscribed",
        )
        read_only_fields = ("is_subscribed",)


class TagsSerializer(serializers.ModelSerializer):
    """Сериализатор для списока тегов"""

    class Meta:
        model = Tag
        fields = "__all__"


class IngredientsSerializer(serializers.ModelSerializer):
    """Сериализатор для списока ингредиентов"""

    class Meta:
        model = Ingredient
        fields = "__all__"


class RecipesReadSerializer(GetIngredientsMixin, serializers.ModelSerializer):
    """Сериализатор для чтения рецептов"""

    tags = TagsSerializer(many=True)
    author = CustomUserListSerializer()
    ingredients = serializers.SerializerMethodField()
    is_favorited = serializers.BooleanField(default=False)
    is_in_shopping_cart = serializers.BooleanField(default=False)

    class Meta:
        model = Recipes
        fields = "__all__"


class RecipesWriteSerializer(GetIngredientsMixin, serializers.ModelSerializer):
    """Сериализатор для записи рецептов"""

    tags = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Tag.objects.all()
    )
    ingredients = serializers.SerializerMethodField()
    image = Base64ImageField()

    class Meta:
        model = Recipes
        fields = "__all__"
        read_only_fields = ("author",)

    def validate(self, data):
        ingredients = self.initial_data["ingredients"]
        ingredient_list = [
            get_object_or_404(Ingredient, id=item["id"])
            for item in ingredients
        ]
        if not ingredients:
            raise serializers.ValidationError(
                "Ингридентов дложно быть не менее одного."
            )
        if len(ingredient_list) != len(set(ingredient_list)):
            raise serializers.ValidationError(
                "Ингредиент уже есть"
            )
        for item in ingredients:
            if int(item.get("amount")) < 1:
                raise serializers.ValidationError(
                    "Минимум должен быть 1 ингридиент"
                )
        data["ingredients"] = ingredients
        return data

    def validate_cooking_time(self, time):
        if int(time) < 1:
            raise serializers.ValidationError(
                "Минимальное время = 1"
            )
        return time

    def add_ingredients_and_tags(self, instance, **validate_data):
        ingredients = validate_data["ingredients"]
        tags = validate_data["tags"]
        for tag in tags:
            instance.tags.add(tag)

        for ingredient in ingredients:
            IngredientInRecipe.objects.create(
                recipe=instance,
                ingredient_id=ingredient.get("id"),
                amount=ingredient.get("amount"),
            )
        return instance

    def create(self, validated_data):
        ingredients = validated_data.pop("ingredients")
        tags = validated_data.pop("tags")
        recipe = super(RecipesWriteSerializer, self).create(validated_data)
        return self.add_ingredients_and_tags(
            recipe, ingredients=ingredients, tags=tags
        )

    def update(self, instance, validated_data):
        instance.ingredients.clear()
        instance.tags.clear()
        ingredients = validated_data.pop("ingredients")
        tags = validated_data.pop("tags")
        instance = self.add_ingredients_and_tags(
            instance, ingredients=ingredients, tags=tags
        )
        return super(RecipesWriteSerializer, self).update(
            instance, validated_data
        )


class RecipeAddingSerializer(serializers.ModelSerializer):
    """Сериализатор для добавления в избранное/список покупок"""

    class Meta:
        model = Recipes
        fields = ("id", "name", "image", "cooking_time")
        read_only_fields = ("id", "name", "image", "cooking_time")


class FollowSerializer(GetIsSubscribedMixin, serializers.ModelSerializer):
    """Сериализатор для подписки"""

    id = serializers.ReadOnlyField(source="author.id")
    email = serializers.ReadOnlyField(source="author.email")
    username = serializers.ReadOnlyField(source="author.username")
    first_name = serializers.ReadOnlyField(source="author.first_name")
    last_name = serializers.ReadOnlyField(source="author.last_name")
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = CustomFollow
        fields = (
            "id",
            "email",
            "username",
            "first_name",
            "last_name",
            "is_subscribed",
            "recipes",
            "recipes_count",
        )

    def get_recipes(self, obj):
        """Получение рецептов автора."""

        request = self.context.get("request")
        limit = request.GET.get("recipes_limit")
        queryset = obj.author.recipes.all().prefetch_related("tags", "author")
        if limit:
            queryset = queryset[: int(limit)]
        return RecipeAddingSerializer(queryset, many=True).data

    def get_recipes_count(self, obj):
        return obj.author.recipes.count()


class CheckFollowSerializer(serializers.ModelSerializer):
    """Сериализатор для проверки подписки"""

    class Meta:
        model = CustomFollow
        fields = ("user", "author")

    def validate(self, obj):
        user = obj["user"]
        author = obj["author"]
        subscribed = user.follower.filter(author=author).exists()
        request_method = self.context["request"].method

        if request_method == "POST":
            if user == author:
                raise serializers.ValidationError(
                    "На себя подписываться нельзя!"
                )
            if subscribed:
                raise serializers.ValidationError("Вы уже подписаны!")
        elif request_method == "DELETE":
            if user == author:
                raise serializers.ValidationError(
                    "Отписаться от себя невозможно!"
                )
            if not subscribed:
                raise serializers.ValidationError(
                    {"errors": "Вы уже отписались!"}
                )

        return obj


class CheckFavouriteSerializer(serializers.ModelSerializer):
    """Сериализатор для проверки избранного."""

    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    recipe = serializers.PrimaryKeyRelatedField(queryset=Recipes.objects.all())

    class Meta:
        model = FavoriteRecipe
        fields = ("user", "recipe")

    def validate(self, obj):
        user = self.context["request"].user
        recipe = obj["recipe"]
        favorite = user.favourites.filter(recipe=recipe).exists()
        request_method = self.context["request"].method

        if request_method == "POST" and favorite:
            raise serializers.ValidationError(
                "Этот рецепт уже есть в избранном"
            )
        elif request_method == "DELETE" and not favorite:
            raise serializers.ValidationError(
                "Этот рецепт отсутствует в избранном"
            )
        return obj


class CheckShoppingCartSerializer(serializers.ModelSerializer):
    """Сериализатор для корзины покупок."""

    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    recipe = serializers.PrimaryKeyRelatedField(queryset=Recipes.objects.all())

    class Meta:
        model = ShoppingCart
        fields = ("user", "recipe")

    def validate(self, obj):
        user = self.context["request"].user
        recipe = obj["recipe"]
        shop_list = user.list.filter(recipe=recipe).exists()
        request_method = self.context["request"].method

        if request_method == "POST" and shop_list:
            raise serializers.ValidationError(
                "Этот рецепт уже в списке покупок."
            )
        elif request_method == "DELETE" and not shop_list:
            raise serializers.ValidationError("Рецепт не в списке покупок.")

        return obj
