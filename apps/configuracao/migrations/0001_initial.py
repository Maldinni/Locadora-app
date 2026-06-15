from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Configuracao",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="criado em")),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="atualizado em")),
                ("nome_locador", models.CharField(blank=True, max_length=150, verbose_name="nome do locador")),
                ("cpf_locador", models.CharField(blank=True, max_length=20, verbose_name="CPF/CNPJ do locador")),
                ("endereco_locador", models.CharField(blank=True, max_length=255, verbose_name="endereço do locador")),
            ],
            options={
                "verbose_name": "configuração",
                "verbose_name_plural": "configurações",
            },
        ),
    ]
