# Generated migration to add timestamp fields

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('djangoldp_story', '0001_initial'),
    ]

    operations = [
        # Add timestamp fields to StoryType model
        migrations.AddField(
            model_name='storytype',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='storytype',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        # Add timestamp fields to StoryObject model
        migrations.AddField(
            model_name='storyobject',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='storyobject',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
