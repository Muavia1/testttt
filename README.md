
Here’s a copy-paste spec you can give your backend engineer.

---

# Backend: Job application statuses – update flow

## 1. Database & model

**Table:** `job`  
**New column:**

| Column name        | Type   | Nullable | Default value |
|--------------------|--------|----------|----------------|
| `applicationStatuses` or `statuses` | JSON   | **NO**   | `["shortlisted", "screening", "interview", "offered", "rejected"]` |

- **Type:** JSON array of strings.
- **Nullable:** `false` — every job must have a value.
- **Default:** Exactly  
  `["shortlisted", "screening", "interview", "offered", "rejected"]`

**Migration:**

- Add the column with the default above.
- Backfill existing rows so no row is null (e.g. set default for all existing jobs when adding the column, or `UPDATE job SET applicationStatuses = default_value WHERE applicationStatuses IS NULL`).

**Model (e.g. Sequelize):**

- Add attribute for this column.
- `allowNull: false`
- `defaultValue: ["shortlisted", "screening", "interview", "offered", "rejected"]`
- Ensure create/read paths use this so all jobs (new and existing) always have this field set.

---

## 2. Existing API: include statuses in job details

**API:** `viewJobPost`  
**Request:** `{ jobId: <number> }` (or existing equivalent).  
**Response:** Existing job object **plus** a top-level field for the status list.

- Add to the job object returned:
  - **Field name:** `statuses` (or `applicationStatuses` — must match what frontend expects).
  - **Value:** The job’s `applicationStatuses` (or `statuses`) column — array of strings, e.g.  
    `["shortlisted", "screening", "interview", "offered", "rejected"]`  
    or the same list with extra values like `"technical_interview"` if the recruiter added them.

No change to auth or other request/response fields; only add this field to the job payload.

---

## 3. New API: update job application statuses

**Purpose:** Recruiter can change the list of application statuses for a job (e.g. add “Technical Interview”, “Second Interview”). Backend replaces the job’s status list with the one sent.

**Endpoint name (suggestion):** `updateJobApplicationStatuses` or `updateJobStatuses`.

**Request:**

- **Method:** POST (or PUT/PATCH if that’s your convention).
- **Body (e.g. JSON):**
  - `jobId` (number, required) — job to update.
  - `statuses` (array of strings, required) — new full list of statuses.  
    Example:  
    `["shortlisted", "screening", "interview", "offered", "rejected", "technical_interview"]`

**Validation:**

- `jobId` must exist and belong to the authenticated user (or company).
- `statuses` must be a non-empty array of strings (no null/undefined entries).
- Optional: max length for the array (e.g. 20) and for each string (e.g. 50 chars).

**Behaviour:**

1. Resolve job by `jobId`, check ownership.
2. Replace the job’s `applicationStatuses` (or `statuses`) column with the received `statuses` array.
3. Return success (and optionally the updated job object including `statuses`).

**Response (example):**

- Success: e.g. `{ status: 200, data: { success: true } }` or return updated job with `statuses`.
- Errors: 4xx for invalid `jobId`, unauthorized, or invalid `statuses`.

---

## 4. Flow summary

| Step | Action |
|------|--------|
| 1 | Add `applicationStatuses` (or `statuses`) column to `job`: JSON, NOT NULL, default `["shortlisted", "screening", "interview", "offered", "rejected"]`. Backfill existing rows. |
| 2 | In **viewJobPost** response, include this field (e.g. as `statuses`) in the job object so every job details response has a status list. |
| 3 | New API **updateJobApplicationStatuses**: accept `jobId` + `statuses` (array of strings); validate; update job’s status list; return success (and optionally updated job). |

---

## 5. Example payloads

**viewJobPost response (snippet):**

```json
{
  "jobId": 123,
  "jobtitle": "...",
  "statuses": ["shortlisted", "screening", "interview", "offered", "rejected"]
}
```

After recruiter adds “Technical Interview” and frontend calls the new API:

**updateJobApplicationStatuses request:**

```json
{
  "jobId": 123,
  "statuses": ["shortlisted", "screening", "interview", "offered", "rejected", "technical_interview"]
}
```

**updateJobApplicationStatuses response (example):**

```json
{
  "status": 200,
  "data": { "success": true }
}
```

You can share this document as-is with your backend engineer; they can implement the migration, viewJobPost change, and the new update API from it.
