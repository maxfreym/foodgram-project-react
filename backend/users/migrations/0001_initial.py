# Generated by Django 4.2.5 on 2023-09-06 14:36

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='CustomFollow',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('follower', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='following_follows', to=settings.AUTH_USER_MODEL, verbose_name='Подписчик')),
                ('following', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='follower_follows', to=settings.AUTH_USER_MODEL, verbose_name='Автор')),
            ],
            options={
                'verbose_name': 'Подписка',
                'verbose_name_plural': 'Подписки',
                'ordering': ('id',),
            },
        ),
        migrations.AddConstraint(
            model_name='customfollow',
            constraint=models.UniqueConstraint(fields=('follower', 'following'), name='unique_customfollow'),
        ),
        migrations.AddConstraint(
            model_name='customfollow',
            constraint=models.CheckConstraint(check=models.Q(('follower', models.F('following')), _negated=True), name='self_subscription_prohibited'),
        ),
    ]
