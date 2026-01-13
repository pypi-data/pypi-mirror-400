# Generated migration for adding timestamp fields to all LDP models
# These fields support HTTP caching headers (Last-Modified, If-Modified-Since)

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('djangoldp_circle', '0037_auto_20231004_1523'),
    ]

    operations = [
        # Add timestamp fields to Circle model
        migrations.AddField(
            model_name='circle',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='circle',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        # Add timestamp fields to CircleMember model
        migrations.AddField(
            model_name='circlemember',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='circlemember',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
