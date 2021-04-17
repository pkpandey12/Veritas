# Generated by Django 3.0.5 on 2021-04-16 20:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Images', '0005_similar_ipfshash'),
    ]

    operations = [
        migrations.RenameField(
            model_name='image',
            old_name='ipfsAddress',
            new_name='imgipfsAddress',
        ),
        migrations.RenameField(
            model_name='image',
            old_name='ipfsHash',
            new_name='imgipfsHash',
        ),
        migrations.AddField(
            model_name='image',
            name='article',
            field=models.TextField(default='Image article'),
        ),
        migrations.AddField(
            model_name='image',
            name='articleipfsHash',
            field=models.CharField(max_length=128, null=True),
        ),
    ]
