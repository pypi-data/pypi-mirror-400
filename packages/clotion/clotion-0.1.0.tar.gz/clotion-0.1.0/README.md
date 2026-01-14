# Clotion

Autonomous development automation with Claude Code and Notion.

Move a Notion card from Backlog to "Todo" and Clotion takes over — it creates an isolated git worktree, runs Claude Code to implement the work, posts progress updates, and opens a PR when done. Move to "Done" and the PR auto-merges.

## Installation

```bash
# 1. Clone the repository
git clone https://github.com/ianborders/clotion.git
cd clotion

# 2. Install the clotion command
pip install clotion

# 3. Create your config
cp .env.example .env
```

Edit `.env` with your API keys (see [Configuration](#configuration) below).

### Updating

```bash
pip install -U clotion
```

## Quick Start

Start Clotion from the cloned directory:

```bash
cd clotion
clotion
```

> **Important:** Always run `clotion` from the cloned repository directory. Configuration is loaded from `.env` in the current working directory.

## How It Works

1. **Move card from Backlog → Todo** — Clotion picks it up
2. **Automatic implementation** — Creates isolated git worktree, runs Claude Code
3. **Progress updates** — Updates "Current Status" property as it works
4. **Blocked?** — Sets "Blocked" checkbox, posts a comment asking for help
5. **Complete** — Pushes code, creates PR, moves to "In Review"
6. **Move to "Done"** — PR auto-merges, worktree cleaned up

## Prerequisites

- Python 3.10+
- [Claude Code](https://claude.ai/code) CLI installed and authenticated
- [GitHub CLI](https://cli.github.com/) (`gh`) installed and authenticated
- Notion workspace with a database/kanban board
- Notion integration with access to your database

## Configuration

Create a `.env` file:

```bash
# Notion Integration
NOTION_API_KEY=secret_xxx           # Your Notion integration token
NOTION_DATABASE_ID=xxx              # ID of your kanban database

# Notion Status Values (must match your Status property options)
NOTION_STATUS_BACKLOG=Backlog
NOTION_STATUS_TODO=Todo
NOTION_STATUS_IN_PROGRESS=In Progress
NOTION_STATUS_IN_REVIEW=In Review
NOTION_STATUS_DONE=Done

# Repository
REPO_PATH=/path/to/your/repo        # The repo Clotion will work on

# Polling
POLL_INTERVAL=5                     # Seconds between checking for changes
```

## Setup

### 1. Create a Notion Integration

1. Go to [Notion Integrations](https://www.notion.so/my-integrations)
2. Click **New integration**
3. Name it "Clotion" and select your workspace
4. Copy the **Internal Integration Token** (starts with `secret_`)
5. Add this token to your `.env` as `NOTION_API_KEY`

### 2. Share Your Database with the Integration

1. Open your Notion database/kanban board
2. Click **Share** in the top right
3. Click **Invite** and select your "Clotion" integration
4. Copy the **Database ID** from the URL:
   - URL format: `notion.so/{workspace}/{database_id}?v=...`
   - The database ID is the 32-character string after your workspace name

### 3. Create the Status Property

Your database needs a **Status** property (Select type) with these options:
- Backlog
- Todo
- In Progress
- In Review
- Done

Clotion will auto-create these additional properties on first run:
- **Blocked** (Checkbox) — Red indicator when Claude needs help
- **Current Status** (Text) — Real-time activity updates
- **Clotion ID** (Text) — Unique task identifier (CLO-001, etc.)
- **Branch** (Text) — Git branch name
- **PR URL** (URL) — Link to GitHub PR

### 4. Run

```bash
clotion
```

Clotion starts polling your Notion database for changes.

## Usage

| Action | Result |
|--------|--------|
| Move card **Backlog → Todo** | Clotion starts working |
| Claude gets stuck | "Blocked" checkbox set, comment posted |
| Reply to comment | Clotion resumes |
| Task complete | PR created, card → "In Review" |
| Move card → **Done** | PR merges, worktree cleaned up |

## Troubleshooting

**Clotion not detecting changes**
- Verify the database is shared with your integration
- Check `NOTION_DATABASE_ID` is correct (32 chars, no dashes)
- Ensure Status property values match exactly

**Claude not starting**
- Run `claude` manually to verify CLI is installed and authenticated
- Check `REPO_PATH` exists and is a git repository

**Tasks stuck with "Blocked" checkbox**
- Check Notion page comments for Claude's question
- Reply to unblock (detected on next poll)

## How It Uses Claude Code

Clotion runs Claude Code CLI in headless mode using your **Claude Code subscription** (not API credits). It's the same Claude you use interactively, just automated.

## License

MIT
