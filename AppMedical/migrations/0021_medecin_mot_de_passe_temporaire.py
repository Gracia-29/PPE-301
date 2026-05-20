from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('AppMedical', '0020_alter_hopital_licence'),
    ]

    operations = [
        migrations.AddField(
            model_name='medecin',
            name='mot_de_passe_temporaire',
            field=models.CharField(blank=True, max_length=100),
        ),
    ]
