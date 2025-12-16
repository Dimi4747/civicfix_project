# Migration pour Like model

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('reports', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Like',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('report', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='likes', to='reports.report')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='likes', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Like',
                'verbose_name_plural': 'Likes',
                'ordering': ['-created_at'],
            },
        ),
        migrations.AddConstraint(
            model_name='like',
            constraint=models.UniqueConstraint(fields=('report', 'user'), name='unique_report_user_like'),
        ),
        migrations.AddIndex(
            model_name='like',
            index=models.Index(fields=['report', '-created_at'], name='reports_like_report_idx'),
        ),
        migrations.AddIndex(
            model_name='like',
            index=models.Index(fields=['user', '-created_at'], name='reports_like_user_idx'),
        ),
    ]
