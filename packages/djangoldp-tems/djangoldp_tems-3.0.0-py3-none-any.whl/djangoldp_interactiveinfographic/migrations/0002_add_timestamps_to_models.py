# Generated migration to add timestamp fields

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('djangoldp_interactiveinfographic', '0001_initial'),
    ]

    operations = [
        # Add timestamp fields to InteractiveInfographicObject model
        migrations.AddField(
            model_name='interactiveinfographicobject',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='interactiveinfographicobject',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
