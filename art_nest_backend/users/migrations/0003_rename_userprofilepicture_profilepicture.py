# Generated by Django 4.2.6 on 2023-11-29 05:29

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_avatar_userprofilepicture_useravatar'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='UserProfilePicture',
            new_name='ProfilePicture',
        ),
    ]
