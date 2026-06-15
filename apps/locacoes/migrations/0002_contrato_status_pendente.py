from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("locacoes", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="locacao",
            name="contrato",
            field=models.FileField(blank=True, null=True, upload_to="contratos/", verbose_name="contrato"),
        ),
        migrations.AddField(
            model_name="locacao",
            name="contrato_gerado_em",
            field=models.DateTimeField(blank=True, null=True, verbose_name="contrato gerado em"),
        ),
        migrations.AlterField(
            model_name="locacao",
            name="status",
            field=models.CharField(
                choices=[
                    ("pendente", "Aguardando contrato"),
                    ("ativo", "Ativo"),
                    ("encerrado", "Encerrado"),
                ],
                db_index=True,
                default="pendente",
                max_length=20,
                verbose_name="status",
            ),
        ),
    ]
