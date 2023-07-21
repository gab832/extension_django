from django.contrib import admin
from connect_ext.recipes.models import (
    Recipe,
    Ingredient,
    Step,
)


class RecipeAdmin(admin.ModelAdmin):
    pass

class IngredientAdmin(admin.ModelAdmin):
    pass

class StepAdmin(admin.ModelAdmin):
    pass


admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Step, StepAdmin)
