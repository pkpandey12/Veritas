# Generated by Django 3.0.5 on 2021-04-12 19:17

from django.db import migrations, models
import django.utils.timezone
import djongo.models.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Text',
            fields=[
                ('_id', djongo.models.fields.ObjectIdField(auto_created=True, primary_key=True, serialize=False, unique=True)),
                ('title', models.CharField(default='Title', max_length=280)),
                ('ipfsHash', models.CharField(max_length=128, null=True)),
                ('ipfsAddress', models.CharField(max_length=128, null=True)),
                ('transactionHash', models.CharField(max_length=128, null=True)),
                ('blockHash', models.CharField(max_length=128, null=True)),
                ('timestamp', models.DateTimeField(default=django.utils.timezone.now, editable=False)),
                ('body', models.TextField()),
            ],
        ),
    ]
