# Generated manually for the demo scaffold.
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='Mechanic',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=120)),
                ('phone', models.CharField(blank=True, max_length=30)),
                ('city', models.CharField(blank=True, max_length=80)),
                ('latitude', models.FloatField(blank=True, null=True)),
                ('longitude', models.FloatField(blank=True, null=True)),
                ('is_available', models.BooleanField(default=True)),
                ('service_radius_km', models.FloatField(default=10)),
            ],
        ),
        migrations.CreateModel(
            name='ServiceRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('customer_name', models.CharField(max_length=120)),
                ('customer_phone', models.CharField(blank=True, max_length=30)),
                ('vehicle_type', models.CharField(default='car', max_length=40)),
                ('issue_type', models.CharField(max_length=120)),
                ('issue_description', models.TextField()),
                ('address', models.CharField(blank=True, max_length=255)),
                ('latitude', models.FloatField()),
                ('longitude', models.FloatField()),
                ('status', models.CharField(choices=[('open', 'Open'), ('accepted', 'Accepted'), ('negotiating', 'Negotiating'), ('completed', 'Completed')], default='open', max_length=20)),
                ('final_price', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('platform_commission', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('assigned_mechanic', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='requests', to='dispatch.mechanic')),
            ],
        ),
        migrations.CreateModel(
            name='Offer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('message', models.TextField(blank=True)),
                ('accepted', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('mechanic', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='offers', to='dispatch.mechanic')),
                ('request', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='offers', to='dispatch.servicerequest')),
            ],
        ),
        migrations.CreateModel(
            name='ChatMessage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sender_name', models.CharField(max_length=120)),
                ('sender_role', models.CharField(choices=[('customer', 'Customer'), ('mechanic', 'Mechanic')], max_length=20)),
                ('message', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('request', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='messages', to='dispatch.servicerequest')),
            ],
        ),
    ]

