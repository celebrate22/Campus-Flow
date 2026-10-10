# CampusFlow

A command-line help desk ticket manager for campus IT support requests.

**Team:** <Fellow A name> (tickets, validation, priority) and <Fellow B name> (assignment, workflow, queue, reports)

## Requirements
Python 3.9+ (standard library only - no installs needed).

## Run
```bash
python main.py
```
Menu: 1 Create, 2 List, 3 View, 4 Assign, 5 Change status, 6 Work queue, 7 Report, 8 Exit.

## Test
```bash
python -m unittest discover -s tests -v
```

## Rules
- **Priority** (first match wins): high + 10+ users = critical; high OR 10+ users = high;
  medium OR 3+ users = medium; otherwise low.
- **Status:** open -> in_progress (needs an assignee) -> resolved. A resolved ticket is locked until reopened to open.
- **Queue:** open tickets, ordered critical -> low, ties by earlier ticket number.

## Data
Tickets are saved in `data/tickets.json`. To start fresh, delete that file.
A corrupted file stops the program with a clear error instead of being overwritten.

## Known limitations
- Single user, text interface only.
- <add your own honest limitations>

## Pull requests
- <link to PR 1>
- <link to PR 2>