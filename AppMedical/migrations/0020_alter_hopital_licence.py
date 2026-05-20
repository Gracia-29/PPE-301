from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('AppMedical', '0019_hopital_structure_fields'),
    ]

    operations = [
        migrations.AlterField(
            model_name='hopital',
            name='licence',
            field=models.FileField(blank=True, null=True, upload_to='licences/'),
        ),
    ]
