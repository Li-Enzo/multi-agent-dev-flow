# <Project Name> · API Contract (API Definition)

> This document is the single source of truth shared by frontend, backend, and QA. Any field added/removed/changed must be synced to the CHANGELOG (see Change Management at the end). Any agent referencing a field must read this document verbatim — never rely on memory.

## 1. General Conventions

### 1.1 Requests

- Gateway entry: `<base URL>`; all interfaces are dispatched by the `action` field or by path.
- Auth header: `Authorization: Bearer <token>`; except for non-login interfaces.
- Unified request body: `{ "action": "<name>", "data": { ... } }`

### 1.2 Unified Response

```json
{ "code": 0, "msg": "ok", "data": { } }
```

| code | Meaning |
| --- | --- |
| 0 | Success |
| 1001 | Invalid parameter |
| 1002 | Not logged in / token expired |
| 1003 | No permission |
| 2001 | Business validation failed (msg carries the specific reason) |
| 2002 | Duplicate submission (idempotency intercept) |
| 3001 | Third-party (payment/push, etc.) error |
| 5000 | System error |

### 1.3 Common Field Conventions

- Money: integer in minor units (cents); time: ISO 8601 UTC strings; pagination: `cursor + limit` (cursor = `createdAt_id`).
- Idempotency: write interfaces accept `idempotencyKey` (retry with the same value returns the original result, code=0).

## 2. <Domain> Domain (example: user)

### 2.x <Interface Name>

| Item | Content |
| --- | --- |
| action | `<name>` |
| Auth | Public / Login required / Permission point `<perm>` required |
| Description | <one sentence> |

**Request Params (data)**

| Field | Type | Required | Meaning | Example |
| --- | --- | --- | --- | --- |
| | string | yes | | |

**Response Params (data)**

| Field | Type | Always present | Meaning | Example |
| --- | --- | --- | --- | --- |

**Error Codes (interface-specific)**

| code | Trigger Condition |
| --- | --- |

---

## N. Change Management

- Field added/removed/changed → update this document + CHANGELOG in the same delivery, with version and date.
- Contract change = the delivery must repackage the documentation pack in the same delivery (bytes of the contract inside the pack match the disk copy; pack time is later than the contract's last modification time).
- Use `scripts/changelog_check.py <this document> <CHANGELOG>` as the automated gatekeeper.
