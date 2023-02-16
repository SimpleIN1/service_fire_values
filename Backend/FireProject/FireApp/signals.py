from django.core.cache import cache
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from models import DateTime, FireValues


# @receiver(post_delete, sender=DateTime)
# def post_delete_date_time(sender, **kwargs):
#     cache.delete('date_time')
#
#
# @receiver(post_save, sender=DateTime)
# def post_delete_date_time(sender, **kwargs):
#     cache.delete('date_time')
#
#
# @receiver(post_save, sender=FireValues)
# def post_save_fire_values(sender, **kwargs):
#     cache.delete('point_data')
#     cache.delete('point_data')
#     cache.delete('point_data')
#     cache.delete('point_data')
#     cache.delete('point_data')
