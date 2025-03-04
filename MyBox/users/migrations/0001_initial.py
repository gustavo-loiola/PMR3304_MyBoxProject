# Generated by Django 5.1.1 on 2024-11-22 14:22

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_type', models.CharField(choices=[('seller', 'Vendedor'), ('buyer', 'Comprador')], default='buyer', max_length=10)),
                ('first_name', models.CharField(default='First Name', max_length=100)),
                ('last_name', models.CharField(default='Last Name', max_length=100)),
                ('cpf', models.CharField(default='000.000.000-00', max_length=14)),
                ('phone', models.CharField(default='(00) 00000-0000', max_length=15)),
                ('address', models.TextField(default='Endereço não informado')),
                ('complement', models.CharField(blank=True, default='Nenhum complemento', max_length=100, null=True)),
                ('cep', models.CharField(default='00000-000', max_length=10)),
                ('birth_date', models.DateField(default='2000-01-01')),
                ('join_date', models.DateField(auto_now_add=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='profile', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Store',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('store_name', models.CharField(max_length=100)),
                ('store_email', models.EmailField(max_length=254, unique=True)),
                ('cnpj', models.CharField(max_length=18, unique=True)),
                ('logo', models.ImageField(blank=True, null=True, upload_to='store_logos/')),
                ('background_image', models.ImageField(blank=True, null=True, upload_to='store_backgrounds/')),
                ('store_description', models.TextField(blank=True, max_length=200, null=True)),
                ('owner', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='store', to='users.profile')),
            ],
        ),
    ]
