# API contracts (Phase 8 / T067)

- **openapi.yaml**: Versioned API reference for frontend integration. Source of truth for documented endpoints and schemas.
- **Schema drift**: To compare the live drf-spectacular schema with this contract, see [quickstart.md](../quickstart.md) section "Schema drift (T067)":
  - `python manage.py spectacular --file /tmp/generated-schema.yaml`
  - `diff specs/001-plots-prosper-core/contracts/openapi.yaml /tmp/generated-schema.yaml`
- Document any intentional drift (extra endpoints, schema extensions) here or in quickstart.
