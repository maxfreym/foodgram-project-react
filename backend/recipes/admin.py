from django.contrib import admin

from .models import (FavoriteRecipe, Ingredient, IngredientInRecipe, Recipes,
                     ShoppingCart, Tag)


class RecipeIngredientInline(admin.StackedInline):
    model = IngredientInRecipe
    min_num = 1


@admin.register(Recipes)
class RecipesAdmin(admin.ModelAdmin):
    list_display = ('name', 'author', 'favorite_count',)
    list_filter = ('name', 'author', 'tags')
    readonly_fields = ('favorite_count',)
    inlines = [RecipeIngredientInline]

    def favorite_count(self, obj):
        return FavoriteRecipe.objects.filter(recipe=obj).count()


@admin.register(Ingredient)
class IngredientsAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    list_filter = ('name',)
    search_fields = ('name',)


@admin.register(Tag)
class TagsAdmin(admin.ModelAdmin):
    list_display = ('name', 'color', 'slug')


@admin.register(FavoriteRecipe)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')
