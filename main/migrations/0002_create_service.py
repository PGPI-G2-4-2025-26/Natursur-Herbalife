from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("main", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name='Appointment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='Name')),
                ('price', models.DecimalField(max_digits=8, decimal_places=2, verbose_name='Price')),
                ('duration', models.PositiveIntegerField(verbose_name='Duration (minutes)')),
                ('description', models.TextField(blank=True, null=True, verbose_name='Description')),
                ('premium', models.BooleanField(default=False, verbose_name='Premium')),
                ('discount', models.DecimalField(max_digits=5, null=True, decimal_places=2, default=0.00, verbose_name='Discount')),
                ('endDiscount', models.DateTimeField(blank=True, null=True, verbose_name='End Discount Date')),

            ],
            options={
                'verbose_name': 'Appointment',
                'verbose_name_plural': 'Appointments',
            },
        ),
    ]
