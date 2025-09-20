from django import template

register = template.Library()

@register.filter
def get_urgency_label(value):
    labels = {
        5: 'Immediate – Production outage, data loss, or business actively losing money/customers',
        4: 'High – Imminent deadline, blocking team, or critical client commitment',
        3: 'Medium – Needed for current sprint/near-term release, or looming event',
        2: 'Low – Can be scheduled for a future sprint/cycle, no negative impact',
        1: 'None – No deadline, can be backlogged indefinitely',
    }
    return labels.get(value, '')

@register.filter
def get_importance_label(value):
    labels = {
        5: 'Critical – Essential for core strategy, major security/legal risk, or unblocks company/flagship launch',
        4: 'High – Significant value to many users, major pain point, or key roadmap item',
        3: 'Medium – Meaningful improvement, highly requested, or moderate technical debt',
        2: 'Low – Minor enhancement, edge-case bug, or small process improvement',
        1: 'Trivial – Cosmetic, no data, or easy workaround exists',
    }
    return labels.get(value, '')
