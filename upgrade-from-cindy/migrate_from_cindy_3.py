# Generated by Django 2.0 on 2018-01-11 03:54

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('sui_hei', '%s'),
    ]

    operations = [
        migrations.CreateModel(
            name='Hint',
            fields=[
                ('id', models.AutoField(max_length=11, primary_key=True, serialize=False)),
                ('content', models.TextField(verbose_name='content')),
                ('puzzle', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='sui_hei.Puzzle')),
                ('created', models.DateTimeField(default=django.utils.timezone.now, verbose_name='created')),
            ],
        ),
        migrations.RemoveField(
            model_name='award',
            name='description_zh_hans',
        ),
        migrations.RemoveField(
            model_name='award',
            name='name_zh_hans',
        ),
        migrations.RenameField(
            model_name='dialogue',
            old_name='askedtime',
            new_name='created',
        ),
    ]
