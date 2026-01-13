# Generated migration for adding timestamp fields to all LDP models
# These fields support HTTP caching headers (Last-Modified, If-Modified-Since)

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('djangoldp_project', '0024_auto_20231013_1440'),
    ]

    operations = [
        # Add timestamp fields to Customer model
        migrations.AddField(
            model_name='customer',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='customer',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        # Add timestamp fields to Project model
        migrations.AddField(
            model_name='project',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='project',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        # Add timestamp fields to BusinessProvider model
        migrations.AddField(
            model_name='businessprovider',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='businessprovider',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        # Add timestamp fields to Member model
        migrations.AddField(
            model_name='member',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='member',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
