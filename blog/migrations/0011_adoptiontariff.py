# Generated for Rêves de Chiens - AdoptionTariff

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0010_sitesettings'),
    ]

    operations = [
        migrations.CreateModel(
            name='AdoptionTariff',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('species', models.CharField(choices=[('chien', 'Chien'), ('chat', 'Chat'), ('rongeur', 'Rongeur'), ('autre', 'Autre')], default='chien', max_length=20, verbose_name='Espèce')),
                ('age_bracket', models.CharField(help_text="Ex: Jusqu'à 11 mois, De 1 à 5 ans...", max_length=150, verbose_name="Tranche d'âge / Catégorie")),
                ('amount', models.DecimalField(decimal_places=2, help_text='Montant en euros', max_digits=6, verbose_name='Tarif (€)')),
                ('notes', models.CharField(blank=True, default='', help_text='Ex: Stérilisation et vaccins compris', max_length=255, verbose_name='Précisions / Inclusions')),
                ('order', models.PositiveIntegerField(default=0, verbose_name="Ordre d'affichage")),
                ('is_active', models.BooleanField(default=True, help_text='Décocher pour masquer ce tarif', verbose_name='Actif')),
            ],
            options={
                'verbose_name': "Tarif d'adoption",
                'verbose_name_plural': "Tarifs d'adoption",
                'ordering': ['species', 'order', 'amount'],
            },
        ),
    ]
