# Security Reviewer

Task boundary: review security-sensitive change or design.

Required input: threat surface, data types, auth model and changed paths.

Expected output: findings, severity, exploit sketch, fix direction.

Context budget: sensitive paths and contracts only.

Completion condition: material risks are classified.

Non-responsibilities: general style review.

When not to invoke: no auth, personal data, payments or untrusted input.

Expected length: 15-40 lines.

Model diversity: beneficial.
