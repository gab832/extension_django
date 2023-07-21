# -*- coding: utf-8 -*-
#
# Copyright (c) 2023, Globex Corporation
# All rights reserved.
#
from connect.client import R
import pytest

from connect_ext.webapp import FastapiDjangoWebApplication


@pytest.mark.django_db
def test_list_recipes(
    test_client_factory,
    recipe_factory,
):
    recipe = recipe_factory()

    client = test_client_factory(FastapiDjangoWebApplication)
    response = client.get('/api/recipes')

    assert response.status_code == 200
    data = response.json()
    assert data == [
        {
            'id': recipe.id,
            'name': recipe.name,
            'origin': recipe.origin,
            'likes': recipe.likes,
            'steps': [],
            'ingredients': [],
        }
    ]
