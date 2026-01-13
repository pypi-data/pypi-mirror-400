# Generated migration for adding timestamp fields to all LDP models
# These fields support HTTP caching headers (Last-Modified, If-Modified-Since)

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('djangoldp_joboffer', '0012_auto_20231016_1908'),
    ]

    operations = [
        # Add timestamp fields to JobOffer model
        migrations.AddField(
            model_name='joboffer',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='joboffer',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
