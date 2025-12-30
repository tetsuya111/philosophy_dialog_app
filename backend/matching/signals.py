from django.db.models.signals import post_save
from django.dispatch import receiver

from accounts.choices import UserMatchingStatus

from .models import Room, WaitingQueue

WAITING_LIMIT_N: int = 4


@receiver(post_save, sender=WaitingQueue)
def add_to_queue(sender, instance, **kwargs) -> None:
    waiting_queue = WaitingQueue.objects.all()
    if waiting_queue.count() >= WAITING_LIMIT_N:
        waiting_queue = waiting_queue[:WAITING_LIMIT_N]
        users = (data.user for data in waiting_queue)
        room = Room()
        room.save()  # 部屋の作成
        room.users.set(users)
        room.save()
        for data in waiting_queue:
            data.delete()  # 待機中のqueueの削除
        for user in users:
            user.matching_status = UserMatchingStatus.NONE
            user.save()
