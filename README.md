# Odyssey Tickets

Unified ticket tracking with a simple 1–10 importance & urgency model, hierarchical work items, comments, and rich activity logging.

## Key Features
- Importance & urgency numeric selects (1 = lowest, 10 = highest) with descriptive option text.
- Derived priority score (importance × urgency) surfaced in the UI & admin for quick sorting (max 100).
- Single `Ticket` model with `ticket_type` (epic, ticket, bug) and self-referential `parent`.
- Asymmetric `related_tickets` relationships for cross-linking.
- Commenting on tickets (records activity entries).
- Activity logging for creations, updates (field diff), and comments.
- Board view grouping by status and by type + client-side type filters (All / Epics / Tickets / Bugs).
- Django admin enhancements (inline editing of importance & urgency, computed priority score column, filtering by type & parent).

## Hierarchy Overview
See `tickets/docs/HIERARCHY.md` for full rationale and rules. Summary:
- Epics: top-level containers, no parent.
- Tickets: standard items, optional epic parent.
- Bugs: must have a ticket parent.
- Validation prevents cycles and enforces parent type constraints.

## Priority Model
Two independent integer fields drive prioritization:
1. Importance (business / strategic impact)
2. Urgency (time sensitivity / blocking pressure)

Scale: 1 (lowest) → 10 (highest). A convenience priority score = importance × urgency (max 100) is displayed but not stored as a separate field (computed in admin and templates). This keeps the mental model transparent and avoids hidden weighting.

Guidance (suggested interpretation):
- Importance 9–10: Mission critical, existential, or major strategic lever.
- Importance 5–8: Meaningful user or revenue impact.
- Importance 1–4: Minor enhancement, low-impact maintenance.
- Urgency 9–10: Act this sprint; external dependency or severe degradation.
- Urgency 5–8: Should schedule soon; growing risk or opportunity window.
- Urgency 1–4: Can defer without near-term consequence.

Because both dimensions are explicit, changing either dimension emits an update activity with a concise diff.

## Comments & Activity
- Adding a comment creates a `commented` activity entry.
- Editing core fields (title, description, status, priority, importance, urgency, type, assignee, parent) creates an `updated` activity summarizing field changes.
- Ticket creation logs a `created` activity.

## Running Tests
```
python manage.py test
```

## Development Notes
- Importance & urgency enforced bounds: 1–10 (10 is highest).
- Priority score = importance × urgency (no persistence column yet; consider denormalizing if sorting at scale becomes hot path).
- CSS class for parent badge: `.ticket-parent-badge` (replaces legacy `.ticket-epic`).
- Migrations 0008–0011 implement the transition from separate `Epic` model to unified hierarchy; 0012 & 0013 handled temporary scale inversions before settling on 10 = highest.

## Future Enhancements (Ideas)
- AJAX endpoint for context-aware parent options.
- Bidirectional related ticket linking helper.
- Constraint-level enforcement (additional DB constraints when on PostgreSQL).
- Inline drag-and-drop reordering within parent scope.
- Denormalized priority_score field + index for large datasets.
- Saved board filter preferences (localStorage already a candidate).

## License
Internal project (license not specified).
