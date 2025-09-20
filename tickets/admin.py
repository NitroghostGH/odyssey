from django import forms
from django.contrib import admin
from django.utils.safestring import mark_safe

from .models import Board, Ticket, TicketActivity
@admin.register(TicketActivity)
class TicketActivityAdmin(admin.ModelAdmin):
    list_display = ('id', 'ticket', 'user', 'activity_type', 'timestamp')
    list_filter = ('user', 'activity_type', 'ticket')


class MatrixWidget(forms.Select):
    IMPORTANCE_DESCRIPTIONS = {
        10: "Critical Business Impact - Complete system failure, severe data loss, or immediate revenue impact",
        9: "Severe Business Risk - Major security vulnerability or compliance violation",
        8: "Strategic Priority - Key business initiative or major feature launch",
        7: "High Value Enhancement - Significant user impact or efficiency improvement",
        6: "Important Feature - Commonly used functionality or moderate user impact",
        5: "Standard Enhancement - Regular feature work or bug fix affecting multiple users",
        4: "Minor Improvement - Quality of life enhancement or limited scope bug",
        3: "Low Priority Task - Nice to have features or cosmetic issues",
        2: "Very Low Impact - Minimal user benefit or extremely rare edge case",
        1: "Trivial - Typos, minor visual tweaks, or documentation updates"
    }
    
    URGENCY_DESCRIPTIONS = {
        10: "Emergency - Active system outage or data loss scenario",
        9: "Critical Timeline - Must be fixed within hours to prevent major issues",
        8: "Urgent Production - Blocking issue affecting multiple teams/customers",
        7: "High Priority - Required for imminent release or deadline",
        6: "Time Sensitive - Needed within current sprint or milestone",
        5: "Normal Priority - Standard development timeline",
        4: "Moderate Timeline - Can wait for next planning cycle",
        3: "Low Urgency - No immediate timeline pressure",
        2: "Background Task - Can be done when convenient",
        1: "No Rush - Can be indefinitely deferred"
    }

    def __init__(self, field_name, *args, **kwargs):
        choices = [(i, str(i)) for i in range(1, 11)]
        super().__init__(choices=choices, *args, **kwargs)
        self.field_name = field_name
        self.descriptions = (
            self.IMPORTANCE_DESCRIPTIONS if field_name == 'importance' 
            else self.URGENCY_DESCRIPTIONS
        )
        
    def render(self, name, value, attrs=None, renderer=None):
        try:
            matrix_html = self.render_matrix(name, value)
            select_html = super().render(name, value, {'style': 'display:none;', **(attrs or {})}, renderer)
            return mark_safe(f'{matrix_html}\n{select_html}')
        except Exception:
            return super().render(name, value, attrs, renderer)
            
    def render_matrix(self, name, value):
        html = f'''
        <div class="matrix-widget" style="margin-bottom:2em;">
            <h4>{self.field_name.capitalize()} Matrix</h4>
            <div style="display:flex; gap:1em;">
                <table border="1" style="border-collapse:collapse;">
                    <tr style="background:#f5f5f5;">
                        <th style="padding:8px;">Level</th>
                        <th style="padding:8px;">Description</th>
                    </tr>'''
        
        # Add rows from 10 to 1 for better visual organization
        for i in range(10, 0, -1):
            color = self.get_level_color(i)
            selected = 'background:#4caf50;color:white;' if str(value) == str(i) else ''
            html += f'''
                    <tr style="border:1px solid #ddd;">
                        <td style="padding:8px;text-align:center;">
                            <button type="button" 
                                onclick="setMatrixAdmin('{name}', {i})" 
                                id="{name}-{i}"
                                style="width:40px;height:40px;border-radius:4px;border:1px solid #ccc;{color}{selected}">
                                {i}
                            </button>
                        </td>
                        <td style="padding:8px;{color}">{self.descriptions[i]}</td>
                    </tr>'''
        
        html += '''
                </table>
            </div>
        </div>'''
        
        html += f'''<script>
function setMatrixAdmin(field, value) {{
    document.getElementById('id_' + field).value = value;
    // Reset all buttons
    for (let i = 1; i <= 10; i++) {{
        let btn = document.getElementById(field + '-' + i);
        if (btn) {{
            btn.style.background = '';
            btn.style.color = '';
        }}
    }}
    // Highlight selected button
    let selectedBtn = document.getElementById(field + '-' + value);
    if (selectedBtn) {{
        selectedBtn.style.background = '#4caf50';
        selectedBtn.style.color = 'white';
    }}
}}
window.addEventListener('DOMContentLoaded', function() {{
    var val = document.getElementById('id_{name}').value;
    setMatrixAdmin('{name}', (val >= 1 && val <= 10) ? val : 1);
}});
</script>'''
        return html
        
    def get_level_color(self, level):
        if level >= 9:
            return 'background:#fef2f2;color:#991b1b;'  # Critical/High
        elif level >= 7:
            return 'background:#fff7ed;color:#9a3412;'  # High/Medium-High
        elif level >= 5:
            return 'background:#f0fdf4;color:#166534;'  # Medium
        elif level >= 3:
            return 'background:#f0f9ff;color:#075985;'  # Medium-Low
        else:
            return 'background:#f8fafc;color:#475569;'  # Low

class TicketAdminForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = '__all__'
        widgets = {
            'importance': MatrixWidget('importance'),
            'urgency': MatrixWidget('urgency'),
        }


@admin.register(Board)
class BoardAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'created_at')
    search_fields = ('name',)

@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    form = TicketAdminForm
    list_display = (
        'id', 'title', 'status', 'priority', 'importance', 'urgency', 'priority_score', 'ticket_type', 'parent', 'board',
        'assignee', 'updated_by', 'created_at', 'updated_at'
    )
    list_editable = ('status', 'priority', 'importance', 'urgency')
    list_filter = (
        'status', 'priority', 'importance', 'urgency', 'ticket_type', 'board', 'updated_by',
        ('parent', admin.EmptyFieldListFilter),  # filter for has/has not parent
    )
    search_fields = ('title', 'description')

    def priority_score(self, obj):
        return obj.importance * obj.urgency
    priority_score.short_description = 'Prio Score'

    def save_model(self, request, obj, form, change):
        if change:  # If this is an edit of an existing object
            old_obj = self.model.objects.get(pk=obj.pk)
            changed_fields = []
            
            # Check which fields have changed
            for field in ['status', 'priority', 'importance', 'urgency', 'ticket_type', 'parent', 'assignee', 'title', 'description']:
                old_value = getattr(old_obj, field)
                new_value = getattr(obj, field)
                if old_value != new_value:
                    changed_fields.append(f"{field}: {old_value} → {new_value}")

            # Set updated_by
            obj.updated_by = request.user
            obj.save()

            # Create activity log if fields changed
            if changed_fields:
                details = "Changed " + ", ".join(changed_fields)
                TicketActivity.objects.create(
                    ticket=obj,
                    user=request.user,
                    action='edited',
                    details=details
                )
        else:  # This is a new ticket
            obj.updated_by = request.user
            obj.save()
            TicketActivity.objects.create(
                ticket=obj,
                user=request.user,
                action='created',
                details='Ticket created'
            )

    def delete_model(self, request, obj):
        # Log deletion before deleting the ticket
        TicketActivity.objects.create(
            ticket=obj,
            user=request.user,
            action='deleted',
            details='Ticket deleted'
        )
        super().delete_model(request, obj)

    def delete_queryset(self, request, queryset):
        # Log bulk deletions
        for obj in queryset:
            TicketActivity.objects.create(
                ticket=obj,
                user=request.user,
                action='deleted',
                details='Ticket deleted in bulk operation'
            )
        super().delete_queryset(request, queryset)
