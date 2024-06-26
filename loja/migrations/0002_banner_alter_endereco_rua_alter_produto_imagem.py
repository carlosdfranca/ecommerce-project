# Generated by Django 5.0.4 on 2024-04-09 13:22

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("loja", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Banner",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("imagem", models.ImageField(blank=True, null=True, upload_to="")),
                (
                    "link_destino",
                    models.CharField(blank=True, max_length=400, null=True),
                ),
                ("ativo", models.BooleanField(default=True)),
            ],
        ),
        migrations.AlterField(
            model_name="endereco",
            name="rua",
            field=models.CharField(blank=True, max_length=400, null=True),
        ),
        migrations.AlterField(
            model_name="produto",
            name="imagem",
            field=models.ImageField(blank=True, null=True, upload_to=""),
        ),
    ]
