# Clockify Manager

GitHub Actions workflow to log time entries to [Clockify](https://clockify.me) via API.

## Setup

### 1. Add secrets to the repository

Go to **Settings → Secrets and variables → Actions** and add:

| Secret | Description |
|---|---|
| `CLOCKIFY_API_KEY` | Your Clockify API key (Profile → API) |
| `CLOCKIFY_WORKSPACE_ID` | *(Optional)* Workspace ID — auto-detected if omitted |

### 2. Run the workflow

Go to **Actions → Log Hours to Clockify → Run workflow** and choose a mode.

---

## Modes

### Single entry

Fill in the form fields:

| Field | Example |
|---|---|
| Date | `2024-01-15` |
| Start time (UTC) | `09:00` |
| End time (UTC) | `17:00` |
| Description | `Backend development` |
| Project | `My Project` *(optional)* |
| Billable | `true` / `false` |

### Batch from file

1. Copy `entries.example.yml` to `entries.yml` (or any path).
2. Fill in your entries.
3. Commit and run the workflow with mode `batch` and the path to your file.

```yaml
# entries.yml
entries:
  - date: "2024-01-15"
    start: "09:00"
    end: "12:30"
    description: "Backend API development"
    project: "My Project"
    billable: true

  - date: "2024-01-15"
    start: "13:30"
    end: "17:00"
    description: "Code review"
    project: "My Project"
    billable: true
```

---

## Local usage

```bash
pip install requests pyyaml

export CLOCKIFY_API_KEY=your_key_here

# Single entry
python scripts/log_hours.py single \
  --date 2024-01-15 --start 09:00 --end 17:00 \
  --description "Development" --project "My Project"

# Batch
python scripts/log_hours.py batch --file entries.yml
```

## Entry fields

| Field | Required | Description |
|---|---|---|
| `date` | Yes | `YYYY-MM-DD` |
| `start` | Yes | `HH:MM` (UTC) |
| `end` | Yes | `HH:MM` (UTC) |
| `description` | Yes | Free text |
| `project` | No | Project name (looked up by name) |
| `project_id` | No | Project ID (alternative to `project`) |
| `billable` | No | `true` / `false` (default: `false`) |
| `tag_ids` | No | List of Clockify tag IDs |
