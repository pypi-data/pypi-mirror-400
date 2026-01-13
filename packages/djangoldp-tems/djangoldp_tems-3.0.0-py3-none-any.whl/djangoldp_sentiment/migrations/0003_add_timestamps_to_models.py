# Generated migration to add timestamp fields

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('djangoldp_sentiment', '0002_remove_sentiment_keywords_sentiment_keyword_and_more'),
    ]

    operations = [
        # Add timestamp fields to SentimentTopic model
        migrations.AddField(
            model_name='sentimenttopic',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='sentimenttopic',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        # Add timestamp fields to Sentiment model
        migrations.AddField(
            model_name='sentiment',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='sentiment',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
