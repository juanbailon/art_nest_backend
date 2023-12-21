# Generated by Django 4.2.6 on 2023-11-15 21:07

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
            name='PasswordResetOTP',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('OTP', models.CharField(max_length=10, unique=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('expires_at', models.DateTimeField(blank=True)),
                ('user_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='FailedPasswordResetOTPAttemps',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('failed_attempts', models.PositiveIntegerField(default=0)),
                ('last_failed_attempt', models.DateTimeField(auto_now_add=True)),
                ('OTP', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='authentication_and_access_management.passwordresetotp')),
            ],
        ),
        migrations.CreateModel(
            name='BlacklistedPasswordResetOTP',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('blacklisted_at', models.DateTimeField(auto_now_add=True)),
                ('OTP', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='authentication_and_access_management.passwordresetotp')),
            ],
        ),
    ]