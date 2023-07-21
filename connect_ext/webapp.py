# -*- coding: utf-8 -*-
#
# Copyright (c) 2023, Globex Corporation
# All rights reserved.
#
from typing import List, Any, Dict
from datetime import timedelta
from copy import copy
from io import StringIO

from django.core.management import call_command
from django.core.handlers.asgi import ASGIHandler
from django.db.models import Sum
from django.db.models.functions import Coalesce
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction

from connect.eaas.core.decorators import (
    router,
    web_app,
    django_secret_key_variable
)
from connect.eaas.core.extension import WebApplicationBase
from fastapi.responses import JSONResponse

from connect_ext.recipes.models import (
    Ingredient,
    Recipe,
    Step,
)
from connect_ext.recipes.utils import (
    RQLFilteredQuerySet,
    RQLLimitOffsetPaginator,
    model_not_found_exception_handler,
)
from connect_ext.recipes.schemas import (
    Recipe as RecipeSchema,
    RecipeCreateOrUpdate as RecipeCreateOrUpdateSchema,
)
from connect_ext.recipes.filters import (
    RecipeFilters,
)


def get_recipes_queryset():
    return Recipe.objects.all().prefetch_related(
        'steps',
        'ingredients',
    ).annotate(
        time=Coalesce(
            Sum(
                'steps__time',
            ),
            timedelta(),
        ),
    )

@django_secret_key_variable('SECRET_KEY')
@web_app(router)
class FastapiDjangoWebApplication(WebApplicationBase):

    @classmethod
    def get_django_asgi_application(cls):
        return ASGIHandler()

    @classmethod
    def get_django_settings(cls, logger, config):
        overrides = {
            'SECRET_KEY': config['SECRET_KEY'],
            'DATABASES': {
                'default': {
                    'ENGINE': 'django.db.backends.postgresql',
                    'HOST': config['DATABASE_HOST'],
                    'PORT': int(config['DATABASE_PORT']),
                    'NAME': config['DATABASE_NAME'],
                    'USER': config['DATABASE_USER'],
                    'PASSWORD': config['DATABASE_PASSWORD'],
                },
            },
        }
        return overrides
    
    @classmethod
    def on_startup(cls, logger, config):
        #os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'connect_ext.fastapi_django.settings')
        result = StringIO()
        call_command('migrate', stdout=result)
        logger.error(f'on_startup: {result.getvalue()}')


    @classmethod
    def get_exception_handlers(cls, exception_handlers: Dict):
        d = copy(exception_handlers)
        d[ObjectDoesNotExist] = model_not_found_exception_handler
        return d

    @router.get(
        '/recipes',
        response_model=List[RecipeSchema],
    )
    async def list_recipes(
        self,
        qs: Any = RQLFilteredQuerySet(RecipeFilters, get_recipes_queryset),
        paginator = RQLLimitOffsetPaginator(),
    ):
        return await paginator.apaginate_queryset(qs, RecipeSchema)

    @router.get(
        '/recipes/{recipe_id}',
        response_model=RecipeSchema,
    )
    async def get_recipe(
        self,
        recipe_id: int,
    ):

        return RecipeSchema.from_orm(
            await get_recipes_queryset().aget(
                pk=recipe_id,
            ),
        )

    def _create_steps(self, recipe, steps):
        for step in steps:
            Step.objects.create(
                recipe=recipe,
                name=step.name,
                position=step.position,
                description=step.description,
                time=step.time,
            )
    
    @router.post(
        '/recipes',
        response_model=RecipeSchema,
    )
    def create_recipe(
        self,
        data: RecipeCreateOrUpdateSchema,
    ):
        with transaction.atomic():
            recipe = Recipe.objects.create(name=data.name, origin=data.origin)
            self._create_steps(recipe, data.steps)
                
            for ingredient in data.ingredients:
                obj, _ = Ingredient.objects.get_or_create(
                    name=ingredient.name,
                )
                recipe.ingredients.add(obj)

        return RecipeSchema.from_orm(
            get_recipes_queryset().get(
                pk=recipe.id,
            ),
        )

    
    @router.put(
        '/recipes/{recipe_id}',
        response_model=RecipeSchema,
    )
    def update_recipe(
        self,
        recipe_id: int,
        data: RecipeCreateOrUpdateSchema,
    ):
        recipe = get_recipes_queryset().get(
            pk=recipe_id,
        )
        
        recipe.name = data.name
        recipe.origin = data.origin if data.origin else recipe.origin
        
        if data.steps:
            recipe.steps.all().delete()
            self._create_steps(recipe, data.steps)

        if data.ingredients:
            current_ingredients = recipe.ingredients.all()
            recipe.ingredients.clear()
            for ingredient in data.ingredients:
                obj, _ = Ingredient.objects.get_or_create(
                    name=ingredient.name,
                )
                recipe.ingredients.add(obj)
            for cingredient in current_ingredients:
                if cingredient.recipes.count() == 0:
                    cingredient.delete()
        
        return RecipeSchema.from_orm(
            get_recipes_queryset().get(
                pk=recipe.id,
            ),
        )

    @router.delete(
        '/recipes/{recipe_id}',
    )
    async def delete_recipe(
        self,
        recipe_id: int,
    ):
        await Recipe.objects.aget(pk=recipe_id)
        await Recipe.objects.filter(pk=recipe_id).adelete()
        return JSONResponse(status_code=204, content=None)
