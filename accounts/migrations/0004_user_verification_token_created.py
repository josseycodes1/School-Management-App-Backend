# Generated by Django 5.0.4 on 2025-07-23 17:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0003_alter_adminprofile_options_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="verification_token_created",
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
