from datetime import timedelta
from typing import List, Any, Optional

from django.utils.duration import duration_string
from django.db.models.query import QuerySet
from pydantic import BaseModel as _BaseModel, validator
from pydantic.utils import GetterDict


class DjangoGetterDict(GetterDict):
    def get(self, key: Any, default: Any = None):
        res = getattr(self._obj, key, default)
        if isinstance(res, QuerySet):
            return list(res)
        return res


class BaseModel(_BaseModel):

    class Config:
        orm_mode = True
        getter_dict = DjangoGetterDict
        underscore_attrs_are_private = True
        json_encoders = {
            timedelta: duration_string,
        }
    
    def dict(self, **kwargs):
        kwargs.pop('exclude_none', None)
        return super().dict(exclude_none=True, **kwargs)



class Step(BaseModel):
    id: Optional[int]
    name: str
    position: int
    description: str
    time: timedelta


class Ingredient(BaseModel):
    id: Optional[int]
    name: str


class Recipe(BaseModel):
    id: int
    name: str
    origin: str
    likes: int
    time: Optional[timedelta]
    steps: Optional[List[Step]]
    ingredients: Optional[List[Ingredient]]

    @validator("steps", pre=True)
    def get_steps(cls, obj: object) -> object:
        return obj if isinstance(obj, list) else list(obj.all())

    @validator("ingredients", pre=True)
    def get_ingredients(cls, obj: object) -> object:
        return obj if isinstance(obj, list) else list(obj.all())
    

class RecipeCreateOrUpdate(BaseModel):
    name: str
    origin: Optional[str]
    steps: List[Step]
    ingredients: List[Ingredient]
