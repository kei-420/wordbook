import string
import random

from .models import PracticeGame
from django.utils.text import slugify


def id_generator(size=60, chars=string.ascii_lowercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


def unique_slug_generator(model_instance, title, slug_field):
    url = slugify(title)
    model_class = model_instance.__class__

    while model_class._default_maanger.filter(url=url).exists():
        object_pk = model_class._default_maanger.latest('pk')
        object_pk = object_pk.pk + 1

        url = f'{url}-{object_pk}'

    return url

