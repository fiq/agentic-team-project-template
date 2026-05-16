---
name: detect-infrastructure
---

# Detect Infrastructure

Separate local topology from deployment target.

Recognise direct process execution, Compose, Testcontainers, AWS, Fly.io, ECS,
EKS, Lambda, S3, RDS, DynamoDB, MSK, SQS/SNS and existing local Kubernetes.

Do not add LocalStack or Kubernetes by default. Use progressive fidelity:

```
fast local loop -> real cheap dependencies -> container integration
  -> deployment smoke -> production verification
```
