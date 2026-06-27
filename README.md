# mac-toolkit

A collection of macOS automation and backup scripts.

## Scripts

### Backups

Automated backup scripts that export data to external storage. All backup scripts create timestamped archives and clean up files older than 30 days.

- **Apple Passwords** (`run_backup_apple_passwords.sh`) - Exports passwords from Apple Passwords CSV to a KeePass database (.kdbx)
- **Apple Contacts** (`run_backup_apple_contacts.sh`) - Exports contacts from macOS Address Book via AppleScript to a zip archive
- **reMarkable Paper Pro** (`run_backup_rmpp.py`) - Downloads documents from a connected reMarkable device via USB web interface

**Setup**: Export data sources to their expected locations (e.g., Apple Passwords CSV to ~/Downloads). Each script validates input before proceeding.

### Utilities

- `scripts/backups/backup_utils.py` - Shared utilities for zipping, cleanup, and backup management
- `scripts/misc/` - Miscellaneous tools and utilities

## Requirements

- Python 3.7+
- macOS (AppleScript and native framework integration)

For Apple Passwords backups: `pip install pykeepass==4.1.1.post1`

## Usage

Run backup scripts directly or via the provided bash wrappers:

```bash
./scripts/backups/run_backup_apple_passwords.sh
./scripts/backups/run_backup_apple_contacts.sh
./scripts/backups/run_backup_rmpp.sh
```

Set the `KDBX_PASSWORD` environment variable to skip the password prompt for Apple Passwords backups.
