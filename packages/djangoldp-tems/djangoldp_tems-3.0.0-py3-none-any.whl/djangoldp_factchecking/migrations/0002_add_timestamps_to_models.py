# Generated migration to add timestamp fields

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('djangoldp_factchecking', '0001_initial'),
    ]

    operations = [
        # Add timestamp fields to FactCheckingAffiliation model
        migrations.AddField(
            model_name='factcheckingaffiliation',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='factcheckingaffiliation',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        # Add timestamp fields to FactCheckingTopic model
        migrations.AddField(
            model_name='factcheckingtopic',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='factcheckingtopic',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        # Add timestamp fields to FactCheckingObject model
        migrations.AddField(
            model_name='factcheckingobject',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='factcheckingobject',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
