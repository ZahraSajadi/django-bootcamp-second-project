# Generated by Django 4.2.11 on 2024-03-08 11:17

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0008_alter_customuser_options"),
    ]

    operations = [
        migrations.AlterField(
            model_name="customuser",
            name="team",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="users.team",
            ),
        ),
    ]
