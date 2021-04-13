# Generated by Django 3.0.5 on 2021-04-10 12:17

from django.db import migrations, models
import django.db.models.deletion
import djongo.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('Images', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Similar',
            fields=[
                ('image_id', djongo.models.fields.ObjectIdField(auto_created=True, primary_key=True, serialize=False)),
                ('percentage', models.FloatField(null=True)),
                ('parent_image', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Images.Image')),
            ],
        ),
    ]