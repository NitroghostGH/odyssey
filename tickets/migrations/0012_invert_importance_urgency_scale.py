from django.db import migrations


def invert_values(apps, schema_editor):
    Ticket = apps.get_model('tickets', 'Ticket')
    for ticket in Ticket.objects.all():
        # old semantics: 10 = highest, 1 = lowest
        # new semantics: 1 = highest, 10 = lowest
        ticket.importance = 11 - ticket.importance
        ticket.urgency = 11 - ticket.urgency
        ticket.save(update_fields=['importance', 'urgency'])


def invert_values_reverse(apps, schema_editor):
    Ticket = apps.get_model('tickets', 'Ticket')
    for ticket in Ticket.objects.all():
        ticket.importance = 11 - ticket.importance
        ticket.urgency = 11 - ticket.urgency
        ticket.save(update_fields=['importance', 'urgency'])


class Migration(migrations.Migration):

    dependencies = [
        ('tickets', '0011_drop_epic_model'),
    ]

    operations = [
        migrations.RunPython(invert_values, invert_values_reverse),
    ]
