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

## CI Image Publishing

The GitHub Actions workflow `CI Build Image` now supports publishing to two registries:

1. GitHub Container Registry (GHCR) – always pushed on non-PR events.
2. (Optional) Amazon Elastic Container Registry (ECR) – pushed only if the required AWS secrets are present.

### GHCR
Images are tagged:
- `<short-sha>` (first 7 characters)
- `<branch-name>` (slashes sanitized to dashes)
- `latest` (only for `main`)

Pull example:
```
docker pull ghcr.io/<owner>/<repo>/odyssey:<short-sha>
```

### Optional ECR Push
To enable ECR tagging & push in the same CI run, add these repository secrets:

Required secrets:
- `AWS_ROLE_TO_ASSUME` – IAM role ARN with ECR push permissions (assumed via GitHub OIDC)
- `AWS_REGION` – e.g. `us-east-1`
- `ECR_REPOSITORY` – Either full ECR URI (`123456789012.dkr.ecr.us-east-1.amazonaws.com/odyssey`) OR just the repo name (`odyssey`).

If you provide only the repository name, the workflow constructs the full URI using the AWS account from the assumed role.

Optional if later extending deployment:
- `ECS_CLUSTER`, `ECS_SERVICE`, `ECS_TASK_FAMILY`, `ECS_EXECUTION_ROLE_ARN`, `ECS_TASK_ROLE_ARN`, `ECS_LOG_GROUP`, `DJANGO_SECRET_KEY`, `ALLOWED_HOSTS`, `DATABASE_URL` (used by the separate deploy workflow, not required for pure image publish).

### How It Works
The workflow always builds & pushes to GHCR. It conditionally:
1. Configures AWS credentials (OIDC assume role) if the core AWS secrets exist.
2. Logs into ECR.
3. Retags the GHCR-built image for ECR and pushes identical tag set (`<short-sha>`, `<branch>`, `latest` on main).

If secrets are missing, ECR steps are skipped cleanly (build still succeeds).

### Verifying ECR Push
After a successful run with ECR enabled:
```
aws ecr list-images --repository-name <repo> --query 'imageIds[?imageTag==`<short-sha>`]' --output table
```

If using only the repo name in `ECR_REPOSITORY`, ensure the role has permissions: `ecr:BatchCheckLayerAvailability`, `ecr:CompleteLayerUpload`, `ecr:GetAuthorizationToken`, `ecr:InitiateLayerUpload`, `ecr:PutImage`, `ecr:UploadLayerPart`, `ecr:DescribeRepositories`, `ecr:CreateRepository` (the last only if you expect auto-creation; otherwise pre-create).

### Minimal IAM Policy Snippet (Push Only)
```json
{
	"Version": "2012-10-17",
	"Statement": [
		{"Effect": "Allow","Action": ["ecr:GetAuthorizationToken"],"Resource": "*"},
		{"Effect": "Allow","Action": [
			"ecr:BatchCheckLayerAvailability","ecr:CompleteLayerUpload","ecr:DescribeImages",
			"ecr:DescribeRepositories","ecr:InitiateLayerUpload","ecr:ListImages",
			"ecr:PutImage","ecr:UploadLayerPart"],"Resource": "*"}
	]
}
```

For locked-down resource ARNs, replace `"Resource": "*"` with the specific repository ARN(s).


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
