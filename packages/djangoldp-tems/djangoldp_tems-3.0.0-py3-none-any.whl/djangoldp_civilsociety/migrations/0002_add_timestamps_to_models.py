# Generated migration to add timestamp fields

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('djangoldp_civilsociety', '0001_initial'),
    ]

    operations = [
        # Add timestamp fields to CivilSocietyType model
        migrations.AddField(
            model_name='civilsocietytype',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='civilsocietytype',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        # Add timestamp fields to CivilSocietyObject model
        migrations.AddField(
            model_name='civilsocietyobject',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='civilsocietyobject',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
