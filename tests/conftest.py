# -*- coding: utf-8 -*-
#
# Copyright (c) 2023, Globex Corporation
# All rights reserved.
#
import os

import pytest
from connect.client import AsyncConnectClient, ConnectClient

from tests.factories import RecipeFactory, StepFactory, IngredientFactory


@pytest.fixture
def connect_client():
    return ConnectClient(
        'ApiKey fake_api_key',
        endpoint='https://localhost/public/v1',
    )


@pytest.fixture
def async_connect_client():
    return AsyncConnectClient(
        'ApiKey fake_api_key',
        endpoint='https://localhost/public/v1',
    )


@pytest.fixture
def logger(mocker):
    return mocker.MagicMock()


@pytest.fixture(scope='function', autouse=True)
def django_db_setup(django_db_setup):
    os.environ.setdefault(
        'DJANGO_SETTINGS_MODULE', 
        'connect_ext.django.settings',
    )
    import django
    django.setup()


@pytest.fixture(scope='session')
def recipe_factory():
    return RecipeFactory


@pytest.fixture(scope='session')
def step_factory():
    return StepFactory


@pytest.fixture(scope='session')
def ingredient_factory():
    return IngredientFactory
