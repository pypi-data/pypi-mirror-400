# Generated migration for adding timestamp fields to all LDP models
# These fields support HTTP caching headers (Last-Modified, If-Modified-Since)

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('djangoldp_onboarding', '0007_registerparticipant_password'),
    ]

    operations = [
        # Add timestamp fields to RegisterParticipant model
        migrations.AddField(
            model_name='registerparticipant',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='registerparticipant',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
