from django.apps import AppConfig


class MatchingConfig(AppConfig):
    name = "matching"

    def ready(self):
        # シグナルを暗黙的に接続（@receiverデコレータ使用時）
        from . import signals  # noqa
