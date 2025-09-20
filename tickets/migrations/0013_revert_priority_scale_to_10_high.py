from django.db import migrations

def revert_values(apps, schema_editor):
    Ticket = apps.get_model('tickets', 'Ticket')
    for t in Ticket.objects.all():
        t.importance = 11 - t.importance
        t.urgency = 11 - t.urgency
        t.save(update_fields=['importance', 'urgency'])

def forward_noop(apps, schema_editor):
    # We intentionally keep this single operation migration reversible by applying the revert in forward.
    # (Because 0012 previously inverted to 1-high; now we flip back to 10-high.)
    revert_values(apps, schema_editor)

class Migration(migrations.Migration):
    dependencies = [
        ('tickets', '0012_invert_importance_urgency_scale'),
    ]
    operations = [
        migrations.RunPython(forward_noop, revert_values),
    ]
