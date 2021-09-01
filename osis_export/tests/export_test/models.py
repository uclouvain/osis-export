from django.db import models


class DummyModel(models.Model):
    name = models.TextField()
    selectable_value = models.TextField(choices=[("A", "A"), ("B", "B"), ("C", "C")])
