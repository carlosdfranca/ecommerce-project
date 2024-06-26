# Generated by Django 5.0.4 on 2024-04-19 18:33

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("loja", "0004_alter_cor_options_alter_tipo_options_categoria_slug_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="Pagamento",
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
                ("id_pedido", models.CharField(max_length=400)),
                ("aprovado", models.BooleanField(default=True)),
                (
                    "pedido",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="loja.pedido",
                    ),
                ),
            ],
        ),
    ]
