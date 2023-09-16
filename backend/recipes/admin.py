from django.contrib import admin
from recipes.models import (Favorite, Follow, Ingredient, Recipe,
                            RecipeIngredient, ShoppingCard, Tag, TagRecipe)


class RecipeIngredientLine(admin.TabularInline):
    model = RecipeIngredient
    min_num = 1


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    inlines = [RecipeIngredientLine]
    list_display = (
        'pk',
        'name',
        'author',
        'cooking_time',
        'pub_date',
        'added_to_favorites_amount'

    )
    list_filter = ('name', 'author', 'tags', 'pub_date', 'cooking_time')
    readonly_fields = ('added_to_favorites_amount',)
    empty_value_display = '-пусто-'

    def added_to_favorites_amount(self, obj):
        return Favorite.objects.filter(recipe=obj).count()

    added_to_favorites_amount.short_description = 'Добавлений в избранное'


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    search_fields = ('name',)
    empty_value_display = '-пусто-'


admin.site.register(Tag)
admin.site.register(TagRecipe)
admin.site.register(RecipeIngredient)
admin.site.register(Follow)
admin.site.register(ShoppingCard)
admin.site.register(Favorite)
