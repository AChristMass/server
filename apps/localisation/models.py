from django.db import models

from ifc.models import PositionModel



class SignalModel(models.Model):
    position = models.ForeignKey(to=PositionModel, on_delete=models.CASCADE)
    bss = models.CharField(max_length=40)
    signal = models.DecimalField(decimal_places=2, max_digits=10)
