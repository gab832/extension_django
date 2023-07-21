import factory


class RecipeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'recipes.Recipe'
        django_get_or_create = ('id',)

    id = None
    name = factory.Faker('word')
    origin = factory.Faker('word')
    likes = 0


class StepFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'recipes.Step'
        django_get_or_create = ('id',)

    id = None
    name = factory.Faker('word')
    position = 1
    description = factory.Faker('word')

    
class IngredientFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'recipes.Ingredient'
        django_get_or_create = ('id',)

    id = None
    name = factory.Faker('word')
