# Generated migration to add timestamp fields

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('djangoldp_object3d', '0001_initial'),
    ]

    operations = [
        # Add timestamp fields to Object3DCategory model
        migrations.AddField(
            model_name='object3dcategory',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='object3dcategory',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        # Add timestamp fields to Object3DFormat model
        migrations.AddField(
            model_name='object3dformat',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='object3dformat',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        # Add timestamp fields to Object3DKeyword model
        migrations.AddField(
            model_name='object3dkeyword',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='object3dkeyword',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        # Add timestamp fields to Object3DObject model
        migrations.AddField(
            model_name='object3dobject',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='object3dobject',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
