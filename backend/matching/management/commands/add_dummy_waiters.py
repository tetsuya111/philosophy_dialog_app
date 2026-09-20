from __future__ import annotations

from typing import TYPE_CHECKING

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from matching.authentication import hash_client_id
from matching.models import GuestClient, WaitingQueue
from matching.services import issue_client, try_form_group

if TYPE_CHECKING:
    from argparse import ArgumentParser


class Command(BaseCommand):
    help = "手動確認用: ダミーのゲストを指定人数だけ待機列に追加する(DEBUG=Trueのときのみ)"

    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument("count", type=int, help="追加する人数")

    def handle(self, *args: object, **options: object) -> None:  # noqa: ARG002
        if not settings.DEBUG:
            msg = "DEBUG=True のときだけ実行できます"
            raise CommandError(msg)
        count = int(str(options["count"]))
        if count < 1:
            msg = "人数は1以上を指定してください"
            raise CommandError(msg)
        for _ in range(count):
            guest = GuestClient.objects.get(client_id_hash=hash_client_id(issue_client()))
            WaitingQueue.objects.create(user=guest.user)
        formed = 0
        while try_form_group() is not None:
            formed += 1
        self.stdout.write(f"ダミーのゲストを{count}人追加しました(成立したグループ: {formed}件)")
