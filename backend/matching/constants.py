from datetime import timedelta

# ランダムコールの設定値。変更はこのファイルだけで行う(.kiro/specs/random-call/)

# マッチングが成立する待機人数
GROUP_SIZE: int = 4

# 待機列に参加してから、マッチングされずに自動で外れるまでの時間
QUEUE_TIMEOUT: timedelta = timedelta(minutes=5)

# 通話ルームの発行から、通話が自動的に終了するまでの有効時間
ROOM_TTL: timedelta = timedelta(minutes=30)

# Jitsiのルーム名の接頭辞(ルーム名は ROOM_NAME_PREFIX + 128bitの乱数)
ROOM_NAME_PREFIX: str = "pd-"
