<<<<<<< HEAD
# Generated by Django 2.1.7 on 2019-03-30 09:19
=======
# Generated by Django 2.1.7 on 2019-03-30 09:58
>>>>>>> (update) User Model

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='mobile',
        ),
    ]
