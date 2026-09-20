from django.core.management.base import BaseCommand

from matching.services import expire_stale


class Command(BaseCommand):
    help = "タイムアウトした待機エントリと、有効時間を過ぎたランダムコールのグループを終了させる(外部スケジューラから定期実行する保険)"

    def handle(self, *args: object, **options: object) -> None:  # noqa: ARG002
        timed_out, expired = expire_stale()
        self.stdout.write(f"タイムアウトした待機エントリ: {timed_out}件 / 満了したグループ: {expired}件")
