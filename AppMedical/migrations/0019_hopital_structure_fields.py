from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('AppMedical', '0018_hopital_email_hopital_statut_alter_customuser_role_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='hopital',
            name='date_expiration',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='hopital',
            name='directeur',
            field=models.CharField(blank=True, max_length=150, null=True),
        ),
        migrations.AddField(
            model_name='hopital',
            name='licence',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='hopital',
            name='nif',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='hopital',
            name='numero_enregistrement',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='hopital',
            name='telephone',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='hopital',
            name='type',
            field=models.CharField(blank=True, choices=[('general', 'General'), ('clinique', 'Clinique'), ('specialise', 'Specialise'), ('centre', 'Centre medical')], max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='hopital',
            name='ville',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
