# Generated manually for Contact model event fields

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('GreenTech', '0003_contact'),
    ]

    operations = [
        migrations.AddField(
            model_name='contact',
            name='event_title',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='contact',
            name='event_type',
            field=models.CharField(blank=True, choices=[('tree_planting', 'Tree Planting'), ('cleanup', 'Cleanup'), ('recycling', 'Recycling'), ('education', 'Environmental Education'), ('conservation', 'Wildlife Conservation'), ('other', 'Other')], max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='contact',
            name='event_date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='contact',
            name='event_time',
            field=models.TimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='contact',
            name='event_location',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='contact',
            name='max_participants',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='contact',
            name='event_description',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='contact',
            name='organizer_name',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='contact',
            name='organizer_phone',
            field=models.CharField(blank=True, max_length=15, null=True),
        ),
        migrations.AddField(
            model_name='contact',
            name='special_requirements',
            field=models.TextField(blank=True, null=True),
        ),
    ] 