from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('seller_id', models.BigIntegerField()),
                ('name', models.CharField(max_length=120)),
                ('description', models.TextField()),
                ('original_price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('sale_price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('condition', models.CharField(max_length=24)),
                ('category', models.CharField(max_length=32)),
                ('images', models.JSONField(default=list)),
                ('weight_kg', models.FloatField(default=1)),
                ('is_on_sale', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Favorite',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_id', models.BigIntegerField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('product', models.ForeignKey(on_delete=models.deletion.CASCADE, related_name='favorites', to='products.product')),
            ],
            options={
                'unique_together': {('user_id', 'product')},
            },
        ),
    ]
