from django.db import models


class UserMatchingStatus(models.IntegerChoices):
    NONE=1      #do nothing
    WATING=2    #waiting for matching
    JOINED=3    #joined into matching