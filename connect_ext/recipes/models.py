from datetime import timedelta

from django.db import models
from django.db.models import Sum


class Recipe(models.Model):
    name = models.CharField('Name', max_length=128)
    origin = models.CharField('Origin', max_length=128, blank=True)
    likes = models.IntegerField('Likes', default=0)

    # @property
    # def total_time(self):
    #     t = await self.steps.aaggregate(total=Sum('time')).get('total', timedelta(0))
    #     t = t if t else timedelta(0)
    #     return f'{t.total_seconds() / 60}min ({await self.steps.all().acount()} step/s)'
    
    # @property
    # def ingredients(self):
    #     return ','.join([ingredient.name for ingredient in self.ingredients.all()])

    def __str__(self):
        return f'{self.name} ({self.origin})'


class Step(models.Model):
    recipe = models.ForeignKey(Recipe, related_name='steps', on_delete=models.CASCADE)
    name = models.CharField('Name', max_length=128)
    position = models.PositiveIntegerField('Position')
    description = models.TextField('Description')
    time = models.DurationField('Time')

    def __str__(self):
        return f'{self.dish.name} = {self.position} - {self.name}'


class Ingredient(models.Model):
    name = models.CharField('Name', max_length=128, unique=True)
    recipes = models.ManyToManyField(Recipe, null=True, blank=True, related_name='ingredients')
    
    def __str__(self):
        return self.name
