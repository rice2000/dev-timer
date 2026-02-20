# dev-timer

A command-line project timer for benchmarking software builds milestone by milestone.

## Features

- Start and stop timed sessions per milestone
- Attach notes when stopping (e.g. what was hard, what worked)
- See a live status of the running timer
- Summary table grouped by project with totals
- Filter summary by project name
- All data stored locally in `timer_data.json`
- Only one timer can run at a time

## Requirements

- Python 3.8+
- pip

## Installation

```bash
git clone https://github.com/rice2000/dev-timer.git
cd dev-timer
pip install -r requirements.txt
```

## Usage

```bash
# Start a timer for a milestone
python3 timer.py start "Testnet wallet MVP" --project "Stellar Wallet"

# Check what's currently running
python3 timer.py status

# Stop the timer with an optional note
python3 timer.py stop --note "Friendbot was tricky, needed 2 fixes"

# Add or update the note on the last completed session
python3 timer.py note "forgot to add this when I stopped"

# View all completed sessions
python3 timer.py summary

# Filter by project
python3 timer.py summary --project "Stellar Wallet"
```

## Example output

```
Project: Stellar Wallet
Milestone                  Duration     Date         Notes
-------------------------  -----------  -----------  -----------------------------------------
Testnet wallet MVP         1h 12m 30s   2026-01-15   Needed 2 fixes on transaction signing
Add mainnet support        0h 22m 10s   2026-01-16   Straightforward once testnet worked
Total                      1h 34m 40s
```
