from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.db import transaction
from django.db.models import BooleanField, Exists, OuterRef, Sum, Value
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from recipes.models import (FavoriteRecipe, Ingredient, IngredientInRecipe,
                            Recipes, ShoppingCart, Tag)
from rest_framework import mixins, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import SAFE_METHODS, IsAuthenticated
from rest_framework.response import Response
from users.models import CustomFollow

from .filters import IngredientsSearchFilter, RecipesFilter
from .permissions import IsAdminAuthorOrReadOnly, IsAdminOrReadOnly
from .serializers import (CheckFavouriteSerializer, CheckFollowSerializer,
                          CheckShoppingCartSerializer, FollowSerializer,
                          IngredientsSerializer, RecipeAddingSerializer,
                          RecipesReadSerializer, RecipesWriteSerializer,
                          TagsSerializer)

User = get_user_model()

FILE_NAME = "shopping-list.txt"
TITLE_SHOP_LIST = "Список покупок с сайта Foodgram:\n\n"


class ListRetrieveViewSet(
    viewsets.GenericViewSet, mixins.ListModelMixin, mixins.RetrieveModelMixin
):
    permission_classes = (IsAdminOrReadOnly,)


class TagsViewSet(ListRetrieveViewSet):
    """Вьюсет для списка тегов"""

    queryset = Tag.objects.all()
    serializer_class = TagsSerializer
    pagination_class = None


class IngredientsViewSet(ListRetrieveViewSet):
    """Вьюсет для ингредиентов"""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientsSerializer
    pagination_class = None
    filter_class = IngredientsSearchFilter


class RecipesViewSet(viewsets.ModelViewSet):
    """Вьюсет для рецептов"""

    permission_classes = (IsAdminAuthorOrReadOnly,)
    filter_class = RecipesFilter

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return RecipesReadSerializer
        return RecipesWriteSerializer

    def get_queryset(self):
        is_authenticated = self.request.user.is_authenticated
        return Recipes.objects.annotate(
            is_favorited=Exists(
                FavoriteRecipe.objects.filter(
                    user=self.request.user, recipe__pk=OuterRef("pk")
                )
            ),
            is_in_shopping_cart=Exists(
                ShoppingCart.objects.filter(
                    user=self.request.user, recipe__pk=OuterRef("pk")
                )
            ),
        ) if is_authenticated else Recipes.objects.annotate(
            is_favorited=Value(False, output_field=BooleanField()),
            is_in_shopping_cart=Value(False, output_field=BooleanField()),
        )

    @transaction.atomic()
    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(
        detail=True, methods=["POST"], permission_classes=(IsAuthenticated,)
    )
    def favorite(self, request, pk=None):
        data = {
            "user": request.user.id,
            "recipe": pk,
        }
        serializer = CheckFavouriteSerializer(
            data=data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        return self.add_object(FavoriteRecipe, request.user, pk)

    @favorite.mapping.delete
    def del_favorite(self, request, pk=None):
        data = {
            "user": request.user.id,
            "recipe": pk,
        }
        serializer = CheckFavouriteSerializer(
            data=data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        return self.delete_object(FavoriteRecipe, request.user, pk)

    @action(
        detail=True, methods=["POST"], permission_classes=(IsAuthenticated,)
    )
    def shopping_cart(self, request, pk=None):
        data = {
            "user": request.user.id,
            "recipe": pk,
        }
        serializer = CheckShoppingCartSerializer(
            data=data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        return self.add_object(ShoppingCart, request.user, pk)

    @shopping_cart.mapping.delete
    def del_shopping_cart(self, request, pk=None):
        data = {
            "user": request.user.id,
            "recipe": pk,
        }
        serializer = CheckShoppingCartSerializer(
            data=data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        return self.delete_object(ShoppingCart, request.user, pk)

    @transaction.atomic()
    def add_object(self, model, user, pk):
        recipe = get_object_or_404(Recipes, id=pk)
        model.objects.create(user=user, recipe=recipe)
        serializer = RecipeAddingSerializer(recipe)
        return Response(serializer.data, status=HTTPStatus.CREATED)

    @transaction.atomic()
    def delete_object(self, model, user, pk):
        model.objects.filter(user=user, recipe__id=pk).delete()
        return Response(status=HTTPStatus.NO_CONTENT)

    @action(
        methods=["GET"], detail=False, permission_classes=(IsAuthenticated,)
    )
    def download_shopping_cart(self, request):
        ingredients = (
            IngredientInRecipe.objects.filter(recipe__list__user=request.user)
            .values("ingredient__name", "ingredient__measurement_unit")
            .order_by("ingredient__name")
            .annotate(total=Sum("amount"))
        )
        result = TITLE_SHOP_LIST
        result += "\n".join(
            (
                f'{ingredient["ingredient__name"]} - {ingredient["total"]}/'
                f'{ingredient["ingredient__measurement_unit"]}'
                for ingredient in ingredients
            )
        )
        response = HttpResponse(result, content_type="text/plain")
        response["Content-Disposition"] = f"attachment; filename={FILE_NAME}"
        return response


class FollowViewSet(UserViewSet):
    """Вьюсет подписок"""

    @action(
        methods=["POST"], detail=True, permission_classes=(IsAuthenticated,)
    )
    @transaction.atomic()
    def subscribe(self, request, id=None):
        user = request.user
        author = get_object_or_404(User, pk=id)
        data = {
            "user": user.id,
            "author": author.id,
        }
        serializer = CheckFollowSerializer(
            data=data,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)
        result = CustomFollow.objects.create(user=user, author=author)
        serializer = FollowSerializer(result, context={"request": request})
        return Response(serializer.data, status=HTTPStatus.CREATED)

    @subscribe.mapping.delete
    @transaction.atomic()
    def del_subscribe(self, request, id=None):
        user = request.user
        author = get_object_or_404(User, pk=id)
        data = {
            "user": user.id,
            "author": author.id,
        }
        serializer = CheckFollowSerializer(
            data=data,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)
        user.follower.filter(author=author).delete()
        return Response(status=HTTPStatus.NO_CONTENT)

    @action(detail=False, permission_classes=(IsAuthenticated,))
    def subscriptions(self, request):
        user = request.user
        queryset = user.follower.all()
        pages = self.paginate_queryset(queryset)
        serializer = FollowSerializer(
            pages, many=True, context={"request": request}
        )
        return self.get_paginated_response(serializer.data)
