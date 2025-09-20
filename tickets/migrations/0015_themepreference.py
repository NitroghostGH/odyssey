from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings

class Migration(migrations.Migration):
    dependencies = [
        ('tickets', '0014_ticketcomment'),
    ]

    operations = [
        migrations.CreateModel(
            name='ThemePreference',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('theme', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='preferred_by', to='tickets.usertheme')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='theme_preference', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
