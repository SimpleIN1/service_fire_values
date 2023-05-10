# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from decimal import Decimal

from django.db import models
# from django.contrib.gis.db import models as gis_models


class DateTime(models.Model):
    datetime = models.DateTimeField(unique=True, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'date_time'


class Subject(models.Model):
    name = models.CharField(max_length=100)
    tag = models.CharField(max_length=10)

    class Meta:
        managed = False
        db_table = 'subject'


class District(models.Model):
    name = models.CharField(max_length=100)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)

    class Meta:
        managed = False
        db_table = 'district'


class Settlement(models.Model):
    name = models.CharField(max_length=70)
    district = models.ForeignKey(District, on_delete=models.CASCADE)
    # point = gis_models.PointField()

    class Meta:
        managed = False
        db_table = 'settlement'


# class Satellite(models.Model):
#     name = models.CharField(max_length=100)
#     tag = models.CharField(max_length=20)
#
#     class Meta:
#         managed = False
#         db_table = 'satellite'


class FireValue(models.Model):
    temperature = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    longitude = models.DecimalField(max_digits=8, decimal_places=5, blank=True, null=True)
    latitude = models.DecimalField(max_digits=8, decimal_places=5, blank=True, null=True)
    datetime = models.ForeignKey(DateTime, models.DO_NOTHING, blank=True, null=True)

    tech = models.BooleanField()

    distance_to_stln = models.DecimalField(max_digits=10, decimal_places=3)
    settlement = models.ForeignKey(Settlement, on_delete=models.CASCADE)
    district = models.ForeignKey(District, on_delete=models.CASCADE)

    # satellite = models.ForeignKey(Satellite, on_delete=models.CASCADE)

    # satellite = Column(String(20))
    # round = Column(Integer)
    # alg_name = Column(String(20))

    satellite = models.CharField(max_length=20)
    round = models.IntegerField()
    alg_name = models.CharField(max_length=20)

    class Directly(models.IntegerChoices):
        N = 1, 'север'
        S = 2, 'юг'
        E = 3, 'восток'
        W = 4, 'запад'
        N_E = 5, 'северо-восток'
        N_W = 6, 'северо-запад'
        S_E = 7, 'юго-восток'
        S_W = 8, 'юго-запад'

    directly_from_stlm = models.PositiveBigIntegerField(choices=Directly.choices)

    class Meta:
        managed = False
        db_table = 'fire_value'


class SettlementFireValue(models.Model):
    settlement = models.ForeignKey(Settlement, on_delete=models.CASCADE)
    fire_value = models.ForeignKey(FireValue, on_delete=models.CASCADE)

    class Meta:
        managed = False
        db_table = 'settlement_fire_value'