from api.filters import IngredientFilter, RecipeFilter
from api.permissions import IsAuthorOrReadOnly
from api.serializers import (CustomUserSerializer, FavoriteSerializer,
                             IngredientSerializer, RecipeReadSerializer,
                             RecipeWriteSerializer, ShoppingCardSerializer,
                             SubscriptionSerializer, TagSerializer)
from core.utils import ListRetrieveModelMixin, get_product_list
from django.conf import settings
from django.db.models import Value
from django.db.models.fields import BooleanField
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from recipes.models import (Favorite, Follow, Ingredient, Recipe, ShoppingCard,
                            Tag)
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from users.models import User


class CustomUserViewSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer
    http_method_names = ['get', 'post', 'delete']

    @action(
        detail=False,
        methods=(['GET']),
        permission_classes=[IsAuthenticated]
    )
    def me(self, request):
        serializer = CustomUserSerializer(request.user,
                                          context={'request': request})
        return Response(serializer.data)

    @action(
        detail=False,
        methods=(['GET']),
        permission_classes=[IsAuthenticated]
    )
    def subscriptions(self, request):
        user = request.user
        subscriptions = Follow.objects.filter(user=user)
        pages = self.paginate_queryset(subscriptions)
        serializer = SubscriptionSerializer(
            pages,
            many=True,
            context={'request': request})
        return self.get_paginated_response(serializer.data)

    @action(
        detail=True,
        methods=(['POST', 'DELETE']),
        permission_classes=[IsAuthenticated]
    )
    def subscribe(self, request, **kwargs):
        if self.request.method == 'POST':
            user = get_object_or_404(User, pk=kwargs.get('id'))
            context = {'request': self.request, 'user': user}
            serializer = SubscriptionSerializer(data=request.data,
                                                context=context)
            if serializer.is_valid(raise_exception=True):
                serializer.save(user=request.user, author=user)
                return Response(data=serializer.data,
                                status=status.HTTP_201_CREATED)
        if self.request.method == 'DELETE':
            user = request.user
            author = get_object_or_404(User, pk=kwargs.get('id'))
            if not Follow.objects.filter(user=user, author=author).exists():
                return Response(
                    {'error': 'Вы не были подписаны на данного пользователя'},
                    status=status.HTTP_400_BAD_REQUEST)
            follow = get_object_or_404(Follow, user=user, author=author)
            follow.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_400_BAD_REQUEST)


class TagListRetrieveViewSet(ListRetrieveModelMixin):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngredientListRetrieveViewSet(ListRetrieveModelMixin):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    filterset_class = IngredientFilter
    filter_backends = (DjangoFilterBackend,)


class RecipeViewSet(viewsets.ModelViewSet):
    http_method_names = ['get', 'post', 'patch', 'delete']
    queryset = Recipe.objects.all()
    permission_classes = [IsAuthorOrReadOnly]
    filterset_class = RecipeFilter
    filter_backends = (DjangoFilterBackend,)

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return Recipe.objects.add_user_annotations(self.request.user.id)
        return Recipe.objects.add_user_annotations(
            Value(None, output_field=BooleanField()))

    def get_serializer_class(self):
        if self.action in ['create', 'partial_update']:
            return RecipeWriteSerializer
        return RecipeReadSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(
        detail=False,
        methods=(['GET']),
        permission_classes=[IsAuthenticated]
    )
    def download_shopping_cart(self, request):
        product_list = get_product_list(request.user)
        response = HttpResponse(product_list,
                                content_type='text/plain')
        response['Content-Disposition'] = (
            f'attachment; filename={settings.FILENAME_SHOPPING_CART}')
        return response

    @action(
        detail=True,
        methods=(['POST', 'DELETE']),
        permission_classes=[IsAuthenticated]
    )
    def shopping_cart(self, request, **kwargs):
        if request.method == 'POST':
            recipe = get_object_or_404(Recipe, pk=kwargs.get('pk'))
            context = {'request': request, 'recipe': recipe}
            serializer = ShoppingCardSerializer(data=request.data,
                                                context=context)
            if serializer.is_valid(raise_exception=True):
                serializer.save(user=request.user, recipe=recipe)
                return Response(data=serializer.data,
                                status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            recipe = get_object_or_404(Recipe, pk=kwargs.get('pk'))
            user = request.user
            if not ShoppingCard.objects.filter(user=user,
                                               recipe=recipe).exists():
                return Response(
                    {'error': 'У вас не было этого рецепта в списке покупок'},
                    status=status.HTTP_400_BAD_REQUEST)
            shopping_card = get_object_or_404(ShoppingCard, user=user,
                                              recipe=recipe)
            shopping_card.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(
        detail=True,
        methods=(['POST', 'DELETE']),
        permission_classes=[IsAuthenticated]
    )
    def favorite(self, request, **kwargs):
        if request.method == 'POST':
            recipe = get_object_or_404(Recipe, pk=kwargs.get('pk'))
            context = {'request': request, 'recipe': recipe}
            serializer = FavoriteSerializer(data=request.data, context=context)
            if serializer.is_valid(raise_exception=True):
                serializer.save(user=request.user, recipe=recipe)
                return Response(data=serializer.data,
                                status=status.HTTP_201_CREATED)
        if request.method == 'DELETE':
            recipe = get_object_or_404(Recipe, pk=kwargs.get('pk'))
            user = request.user
            if not Favorite.objects.filter(user=user, recipe=recipe).exists():
                return Response(
                    {'error': 'У вас не было этого рецепта в избранном'},
                    status=status.HTTP_400_BAD_REQUEST)
            favorite_recipe = get_object_or_404(Favorite, user=user,
                                                recipe=recipe)
            favorite_recipe.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_400_BAD_REQUEST)
