# Generated by Django 5.1.6 on 2025-03-07 00:31

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='OAuthConfig',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(choices=[('weibo', 'weibo'), ('google', 'google'), ('github', 'GitHub'), ('facebook', 'FaceBook'), ('qq', 'QQ')], default='a', max_length=10, verbose_name='type')),
                ('appkey', models.CharField(max_length=200, verbose_name='AppKey')),
                ('appsecret', models.CharField(max_length=200, verbose_name='AppSecret')),
                ('callback_url', models.CharField(default='', max_length=200, verbose_name='callback url')),
                ('is_enable', models.BooleanField(default=True, verbose_name='is enable')),
                ('creation_time', models.DateTimeField(default=django.utils.timezone.now, verbose_name='creation time')),
                ('last_modify_time', models.DateTimeField(default=django.utils.timezone.now, verbose_name='last modify time')),
            ],
            options={
                'verbose_name': 'oauth配置',
                'verbose_name_plural': 'oauth配置',
                'ordering': ['-creation_time'],
            },
        ),
        migrations.CreateModel(
            name='OAuthUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('openid', models.CharField(max_length=50)),
                ('nickname', models.CharField(max_length=50, verbose_name='nick name')),
                ('token', models.CharField(blank=True, max_length=150, null=True)),
                ('picture', models.CharField(blank=True, max_length=350, null=True)),
                ('type', models.CharField(max_length=50)),
                ('email', models.CharField(blank=True, max_length=50, null=True)),
                ('metadata', models.TextField(blank=True, null=True)),
                ('creation_time', models.DateTimeField(default=django.utils.timezone.now, verbose_name='creation time')),
                ('last_modify_time', models.DateTimeField(default=django.utils.timezone.now, verbose_name='last modify time')),
                ('author', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='author')),
            ],
            options={
                'verbose_name': 'oauth user',
                'verbose_name_plural': 'oauth user',
                'ordering': ['-creation_time'],
            },
        ),
    ]
