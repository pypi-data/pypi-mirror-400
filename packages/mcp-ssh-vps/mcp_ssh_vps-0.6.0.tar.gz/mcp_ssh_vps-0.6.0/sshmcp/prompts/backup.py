"""MCP Prompt for database backup."""


def backup_database(
    host: str,
    database_name: str,
    database_type: str = "postgresql",
    backup_path: str = "/var/backups",
    compress: bool = True,
) -> str:
    """
    Generate database backup prompt.

    Creates a step-by-step backup plan for a database.

    Args:
        host: Target host name.
        database_name: Name of the database to backup.
        database_type: Database type (postgresql, mysql, mongodb).
        backup_path: Directory for backup files.
        compress: Whether to compress the backup.

    Returns:
        Backup instructions as multi-line string.
    """
    # Build backup command based on database type
    timestamp = "$(date +%Y%m%d_%H%M%S)"

    if database_type == "postgresql":
        dump_cmd = f"pg_dump {database_name}"
        backup_file = f"{backup_path}/{database_name}_{timestamp}.sql"
        if compress:
            dump_cmd = f"pg_dump {database_name} | gzip"
            backup_file = f"{backup_path}/{database_name}_{timestamp}.sql.gz"
        dump_full = f"{dump_cmd} > {backup_file}"
        verify_cmd = f"{'zcat' if compress else 'head -20'} {backup_file}"

    elif database_type == "mysql":
        dump_cmd = f"mysqldump {database_name}"
        backup_file = f"{backup_path}/{database_name}_{timestamp}.sql"
        if compress:
            dump_cmd = f"mysqldump {database_name} | gzip"
            backup_file = f"{backup_path}/{database_name}_{timestamp}.sql.gz"
        dump_full = f"{dump_cmd} > {backup_file}"
        verify_cmd = f"{'zcat' if compress else 'head -20'} {backup_file}"

    elif database_type == "mongodb":
        backup_file = f"{backup_path}/{database_name}_{timestamp}"
        dump_full = f"mongodump --db {database_name} --out {backup_file}"
        if compress:
            dump_full = (
                f"mongodump --db {database_name} --archive={backup_file}.gz --gzip"
            )
            backup_file = f"{backup_file}.gz"
        verify_cmd = f"ls -la {backup_file}"

    else:
        dump_full = f"echo 'Unknown database type: {database_type}'"
        backup_file = "unknown"
        verify_cmd = "echo 'Cannot verify'"

    # Build connectivity check command
    if database_type == "postgresql":
        conn_check = 'psql -c "SELECT 1"'
    elif database_type == "mysql":
        conn_check = 'mysql -e "SELECT 1"'
    else:
        conn_check = 'mongosh --eval "db.runCommand({ping: 1})"'

    return f"""Backup database {database_name} on {host}:

## Pre-backup Checks

1. Check server status and disk space:
   - Use get_status resource for {host}
   - Use get_metrics resource for {host} to check disk space
   ```
   execute_command(host="{host}", command="df -h {backup_path}")
   ```

2. Ensure backup directory exists:
   ```
   execute_command(host="{host}", command="mkdir -p {backup_path}")
   ```

3. Check database connectivity:
   ```
   execute_command(host="{host}", command="{conn_check}")
   ```

## Backup Steps

4. Create database dump:
   ```
   execute_command(host="{host}", command="{dump_full}", timeout=600)
   ```

5. Verify backup file was created:
   ```
   execute_command(host="{host}", command="ls -la {backup_file}")
   ```

6. Verify backup integrity:
   ```
   execute_command(host="{host}", command="{verify_cmd}")
   ```

## Post-backup Tasks

7. Calculate backup checksum:
   ```
   execute_command(host="{host}", command="md5sum {backup_file}")
   ```

8. Clean up old backups (keep last 7):
   ```
   execute_command(host="{host}", command="ls -t {backup_path}/{database_name}_* | tail -n +8 | xargs -r rm")
   ```

9. List current backups:
   ```
   execute_command(host="{host}", command="ls -la {backup_path}/{database_name}_*")
   ```

## Backup Details
- Database: {database_name}
- Type: {database_type}
- Backup path: {backup_path}
- Compression: {"Enabled (gzip)" if compress else "Disabled"}
- Expected file: {backup_file}

## Restore Command (for reference)
{_get_restore_command(database_type, database_name, backup_file)}
"""


def _get_restore_command(db_type: str, db_name: str, backup_file: str) -> str:
    """Get restore command for database type."""
    if db_type == "postgresql":
        if backup_file.endswith(".gz"):
            return f"gunzip -c {backup_file} | psql {db_name}"
        return f"psql {db_name} < {backup_file}"
    elif db_type == "mysql":
        if backup_file.endswith(".gz"):
            return f"gunzip -c {backup_file} | mysql {db_name}"
        return f"mysql {db_name} < {backup_file}"
    elif db_type == "mongodb":
        if backup_file.endswith(".gz"):
            return f"mongorestore --db {db_name} --archive={backup_file} --gzip"
        return f"mongorestore --db {db_name} {backup_file}"
    return "# Unknown database type"
