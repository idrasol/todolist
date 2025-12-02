# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('collaboration', '0004_alter_post_color'),
    ]

    operations = [
        migrations.AddField(
            model_name='board',
            name='is_public',
            field=models.BooleanField(default=True, verbose_name='공개 여부'),
        ),
        migrations.AddField(
            model_name='post',
            name='z_index',
            field=models.IntegerField(default=1, verbose_name='레이어 순서'),
        ),
        migrations.AddField(
            model_name='post',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='posts/', verbose_name='이미지'),
        ),
    ]





