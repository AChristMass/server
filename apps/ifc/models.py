from django.contrib.postgres.fields import JSONField
from django.db import models

# Create your models here.


class IFCModel(models.model):
    graph = JSONField(null=False, default=dict)
    
    @classmethod
    def parse(cls, filename):
        pass
