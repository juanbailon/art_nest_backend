# Generated by Django 4.2.6 on 2023-11-20 07:21

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('authentication_and_access_management', '0002_alter_failedpasswordresetotpattemps_last_failed_attempt'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='FailedPasswordResetOTPAttemps',
            new_name='FailedPasswordResetOTPAttempts',
        ),
    ]
