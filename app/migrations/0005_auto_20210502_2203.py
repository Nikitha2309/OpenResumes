# Generated by Django 3.1.2 on 2021-05-02 16:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0004_auto_20210430_2333'),
    ]

    operations = [
        migrations.AlterField(
            model_name='resume',
            name='latexFile',
            field=models.CharField(max_length=40),
        ),
        migrations.AlterField(
            model_name='resume',
            name='pdfFile',
            field=models.CharField(default='default', max_length=40),
            preserve_default=False,
        ),
    ]
