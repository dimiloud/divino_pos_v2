from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('description', models.TextField(blank=True)),
                ('active', models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name='Sale',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('reference', models.CharField(max_length=10, unique=True)),
                ('payment_method', models.CharField(choices=[('CASH', 'Espèces'), ('CARD', 'Carte')], max_length=10)),
                ('notes', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('cashier', models.ForeignKey(on_delete=models.PROTECT, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
