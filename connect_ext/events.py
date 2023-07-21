from django.conf import settings
from django.core.handlers.asgi import ASGIHandler
from connect.eaas.core.decorators import schedulable
from connect.eaas.core.extension import EventsApplicationBase
from connect.eaas.core.responses import BackgroundResponse

from connect_ext.recipes.models import Recipe
from connect_ext.recipes.schemas import Recipe as RecipeSchema


class E2EEventsApplication(EventsApplicationBase):

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

    @schedulable(
        'Calculate top 5',
        'It is used to calculate top 5 scheduler.',
    )
    async def calculate_top_5(self, request):
        top_5 = RecipeSchema.from_orm(Recipe.objects.all().order_by('likes')[:5])
        return BackgroundResponse.done()

    #todo: schedule task that will show the top 5 most recepit (likes)
