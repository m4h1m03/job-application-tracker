# Job Application Tracker

A Python and SQLite command-line project for tracking job applications, statuses, and notes.

## Features
- Add job applications
- Store company, role, status, date applied, and job link
- Update application status
- Add notes to applications
- View and manage records from the command line

## Tools Used
- Python
- SQLite
- argparse

## Purpose
I built this project to improve my Python, SQL, and database skills while creating a practical tool for managing job applications.

## File Overview
- `apptrack_v2.py` - main Python script
- `.gitignore` - ignores database and system files

## Notes
This repository contains the project code only. Personal job application data is not included.

## Example Commands
```bash
python apptrack_v2.py add
python apptrack_v2.py add --company "Example Company" --role "Graduate Engineer" --status "Applied" --job_link "https://example.com/job"
python apptrack_v2.py list
python apptrack_v2.py update 1 --status "Interview"
python apptrack_v2.py update 1 --notes "Invited to first interview"
python apptrack_v2.py delete 1


## Test
This is a test commit to practice the Git push workflow.