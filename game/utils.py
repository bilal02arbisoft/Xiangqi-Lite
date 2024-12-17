from django.conf import settings
from hashids import Hashids

salt = settings.SECRET_KEY
hashids = Hashids(salt=salt, min_length=6)
