# Generated by Django 4.2.6 on 2023-11-29 07:00

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_rename_userprofilepicture_profilepicture'),
    ]

    operations = [
        migrations.RenameField(
            model_name='avatar',
            old_name='avatar_image',
            new_name='image',
        ),
        migrations.RenameField(
            model_name='avatar',
            old_name='avatar_name',
            new_name='name',
        ),
    ]
