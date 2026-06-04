# Data Retention Policy

- Personal data is retained for **90 days**, then hard-deleted (GDPR Art. 17; ticket PRIV-88).
- The deletion job runs nightly at 02:00 UTC and is irreversible.
- Backups are purged within **35 days** (legal maximum — do not extend).
- Reading the deletion audit logs requires the `auditor` role.
