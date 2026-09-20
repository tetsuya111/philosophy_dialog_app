# ランダムコール(.kiro/specs/random-call/)のためのモデル変更。
# 既存の WaitingQueue / Room の行は開発用データであり、新しい制約・必須項目を満たせないため先に削除する。

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


def delete_existing_rows(apps, schema_editor):
    apps.get_model("matching", "WaitingQueue").objects.all().delete()
    apps.get_model("matching", "Room").objects.all().delete()


class Migration(migrations.Migration):
    dependencies = [
        ("matching", "0003_waitingqueue"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RunPython(delete_existing_rows, migrations.RunPython.noop),
        migrations.RemoveField(model_name="room", name="users"),
        migrations.AlterField(
            model_name="room",
            name="created_at",
            field=models.DateTimeField(auto_now_add=True, db_comment="作成日時"),
        ),
        migrations.AddField(
            model_name="room",
            name="room_name",
            field=models.CharField(db_comment="Jitsiのルーム名", default="", max_length=64, unique=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="room",
            name="status",
            field=models.CharField(choices=[("active", "Active"), ("ended", "Ended")], db_comment="状態", default="active", max_length=10),
        ),
        migrations.AddField(
            model_name="room",
            name="end_reason",
            field=models.CharField(blank=True, choices=[("all_left", "All Left"), ("expired", "Expired")], db_comment="終了理由", max_length=10),
        ),
        migrations.AddField(
            model_name="room",
            name="expires_at",
            field=models.DateTimeField(db_comment="有効期限", default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="room",
            name="ended_at",
            field=models.DateTimeField(blank=True, db_comment="終了日時", null=True),
        ),
        migrations.AddIndex(
            model_name="room",
            index=models.Index(fields=["status", "expires_at"], name="matching_ro_status_36b30d_idx"),
        ),
        migrations.AlterModelOptions(name="waitingqueue", options={"ordering": ["created_at", "id"]}),
        migrations.AlterField(
            model_name="waitingqueue",
            name="created_at",
            field=models.DateTimeField(auto_now_add=True, db_comment="作成日時"),
        ),
        migrations.AlterField(
            model_name="waitingqueue",
            name="user",
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="waiting", to=settings.AUTH_USER_MODEL),
        ),
        migrations.CreateModel(
            name="GuestClient",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("client_id_hash", models.CharField(db_comment="利用者識別子のSHA-256", max_length=64, unique=True)),
                ("created_at", models.DateTimeField(auto_now_add=True, db_comment="作成日時")),
                ("user", models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="guest_client", to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name="RoomMember",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("is_active", models.BooleanField(db_comment="このメンバー行が現在ユーザーを拘束しているか", default=True)),
                ("joined_at", models.DateTimeField(blank=True, db_comment="初回入室日時", null=True)),
                ("left_at", models.DateTimeField(blank=True, db_comment="満了前の通話終了日時", null=True)),
                ("room", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="members", to="matching.room")),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="room_memberships", to=settings.AUTH_USER_MODEL)),
            ],
            options={
                "constraints": [
                    models.UniqueConstraint(fields=("room", "user"), name="unique_room_member"),
                    models.UniqueConstraint(condition=models.Q(("is_active", True)), fields=("user",), name="one_active_room_per_user"),
                ],
            },
        ),
    ]
