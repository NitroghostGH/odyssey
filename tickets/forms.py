from django import forms
from .models import Ticket

class TicketForm(forms.ModelForm):
    ticket_type = forms.ChoiceField(choices=Ticket.TICKET_TYPE_CHOICES, required=True)
    parent = forms.ModelChoiceField(
        queryset=Ticket.objects.none(),  # dynamically set in __init__ based on type
        required=False,
        help_text='Parent ticket (Epic for tickets, Ticket for bugs).'
    )

    # Descriptive ranking labels (10 is highest)
    IMPORTANCE_CHOICES = [
        (1, '1 – Trivial (Little to no impact)'),
        (2, '2 – Minor (Low impact)'),
        (3, '3 – Low (Nice to have)'),
        (4, '4 – Somewhat Important'),
        (5, '5 – Moderate Value'),
        (6, '6 – Above Average Value'),
        (7, '7 – Important (Clear business value)'),
        (8, '8 – Very Important (High value)'),
        (9, '9 – Essential (Critical for objectives)'),
        (10, '10 – VITAL (Mission critical)'),
    ]
    # Urgency now framed as "time remaining before it must be done" (10 = right now)
    URGENCY_CHOICES = [
        (1, '1 – No time constraint (Backlog / whenever)'),
        (2, '2 – > 1 Quarter (Far future – schedule later)'),
        (3, '3 – 1–3 Months (Long runway)'),
        (4, '4 – Several Weeks (Plan in upcoming cycles)'),
        (5, '5 – 1–2 Weeks (Should land this or next sprint)'),
        (6, '6 – A Few Days (Needs attention soon)'),
        (7, '7 – This Week (Time shrinking)'),
        (8, '8 – Next 1–2 Days (High pressure)'),
        (9, '9 – Today (Very urgent – prioritize)'),
        (10, '10 – NOW (Immediate action required)'),
    ]

    class Meta:
        model = Ticket
        fields = [
            'title', 'description', 'status', 'priority', 'importance', 'urgency',
            'ticket_type', 'parent', 'assignee', 'board'
        ]
        # Importance & urgency now shown as normal selects (no matrix widget)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Replace integer inputs with descriptive selects
        self.fields['importance'] = forms.ChoiceField(
            choices=self.IMPORTANCE_CHOICES,
            required=True,
            label='Importance (1-10)'
        )
        self.fields['urgency'] = forms.ChoiceField(
            choices=self.URGENCY_CHOICES,
            required=True,
            label='Urgency (1-10 – Time Pressure)',
            help_text='How soon does this require completion? 10 = now / immediate, 1 = no defined deadline.'
        )

        # Pre-select existing numeric values if editing
        if self.instance and self.instance.pk:
            self.initial.setdefault('importance', self.instance.importance)
            self.initial.setdefault('urgency', self.instance.urgency)

        # Determine ticket_type from data or instance (default ticket)
        t_type = None
        if self.data.get('ticket_type'):
            t_type = self.data.get('ticket_type')
        elif self.instance and self.instance.pk:
            t_type = self.instance.ticket_type
        else:
            t_type = 'ticket'
        # Filter parent queryset based on desired parent type
        if t_type == 'ticket':
            self.fields['parent'].queryset = Ticket.objects.filter(ticket_type='epic')
        elif t_type == 'bug':
            self.fields['parent'].queryset = Ticket.objects.filter(ticket_type='ticket')
        else:  # epic
            self.fields['parent'].queryset = Ticket.objects.none()
        # If epic, hide parent field visually (optional; template may handle)
        if t_type == 'epic':
            self.fields['parent'].widget = forms.HiddenInput()
