# Generated migration to add timestamp fields

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('djangoldp_mediaobject', '0001_initial'),
    ]

    operations = [
        # Add timestamp fields to MediaObjectCategory model
        migrations.AddField(
            model_name='mediaobjectcategory',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='mediaobjectcategory',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        # Add timestamp fields to MediaObjectFormat model
        migrations.AddField(
            model_name='mediaobjectformat',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='mediaobjectformat',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        # Add timestamp fields to MediaObjectAsset model
        migrations.AddField(
            model_name='mediaobjectasset',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='mediaobjectasset',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        # Add timestamp fields to MediaObjectKeyword model
        migrations.AddField(
            model_name='mediaobjectkeyword',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='mediaobjectkeyword',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        # Add timestamp fields to MediaObjectLanguage model
        migrations.AddField(
            model_name='mediaobjectlanguage',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='mediaobjectlanguage',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
