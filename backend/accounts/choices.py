from django.db import models


class UserMatchingStatus(models.IntegerChoices):
    NONE = 0  # do nothing
    WATING = 1  # waiting for matching
    JOINED = 2  # joined into matching
