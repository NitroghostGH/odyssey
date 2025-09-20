# Ticket Hierarchy & Types

The system uses a single `Ticket` model to represent all work items. Hierarchy and semantics are expressed via two fields:

- `ticket_type`: one of `epic`, `ticket`, `bug`.
- `parent`: nullable self-referential FK to another `Ticket`.

## Rules (Enforced in `Ticket.clean()`)
1. Epics cannot have a parent.
2. Tickets (standard) may have an epic as parent or be top-level (no parent) – business rule currently allows both.
3. Bugs must have a parent whose `ticket_type` is `ticket`.
4. No cycles permitted in the ancestry chain.
5. Importance & urgency are bounded integers 1–10 (10 = highest).

## Rationale
Historically Epics were a separate model referenced by `Ticket.epic`. This created duplication and a complex migration path for adding deeper hierarchy (bugs) and cross-linking. Converging on a single model:
- Simplifies queries & admin.
- Enables arbitrary depth extension in future (e.g., sub-task) with minimal schema change (potentially by widening allowed parent types).
- Removes special-case creation UI and form branching.

## Migration Path Summary
1. Added new columns (`ticket_type`, `parent`, `related_tickets`).
2. Backfilled `ticket_type` based on legacy `epic` FK presence.
3. Converted legacy `Epic` rows into `Ticket` rows of `ticket_type='epic'` and reassigned relationships.
4. Dropped `Ticket.epic` FK and deleted the `Epic` model.

## Related Tickets
`related_tickets` is an asymmetric many-to-many used for lightweight association (e.g., duplicates, blocks). Bidirectional semantics are not auto-enforced – callers add reverse links when desired.

## Admin & UI Notes
- Parent badge on cards now uses CSS class `ticket-parent-badge` (replaces legacy `.ticket-epic`).
- Creation & edit form dynamically hides the parent selector when `ticket_type='epic'`.
- Importance & urgency are simple selects (matrix widget retired) with descriptive labels; a derived priority score (importance × urgency) is shown alongside but not stored.
- Future enhancement: server-side filtered parent options via AJAX (current approach filters client-side heuristically).

## Extensibility
To add a new level (e.g., `subtask`):
1. Add new choice to `ticket_type` enum.
2. Extend validation matrix in `clean()` to define allowed parent types.
3. Adjust form JS to handle visibility/parent filtering.
4. Add tests mirroring those in `test_hierarchy.py`.

## Testing
Hierarchy behaviors covered in `tickets/tests/test_hierarchy.py` plus creation & view tests. Always run the full suite before and after structural changes:

```
python manage.py test tickets.tests -v 2
```

## Integrity Guarantees
- Application-level validation prevents invalid parent assignments & cycles.
- DB-level referential integrity ensures parent existence.
- Consider adding conditional constraints in the future (e.g., partial indexes) if moving to PostgreSQL for stricter enforcement at the database layer.
