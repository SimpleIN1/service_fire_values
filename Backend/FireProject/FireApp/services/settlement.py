from FireApp.models import Settlement


def get_settlement():
    return Settlement.objects.all().values('id', 'name')