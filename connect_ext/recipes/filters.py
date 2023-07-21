from dj_rql.filter_cls import RQLFilterClass

from connect_ext.recipes.models import (
    Recipe,
)


class RecipeFilters(RQLFilterClass):
    MODEL = Recipe
    FILTERS = (
        {
            'filter': 'name',
            'ordering': True,
        },
        {
            'filter': 'origin',
            'ordering': True,
        },
        {
            'filter': 'likes',
            'ordering': True,
        },
        {
            'filter': 'ingredients.name',
            'source': 'ingredients__name',
        },
    )
