- Better load generator with more realistic loads
- Grafana dashboard is pre-built, a custom one would be better
- Grafana alerts

- Version pinning, I used latest in most of them but they should be pinned to a stable release
- Extended Healthchecks, I only added this for the main postgres service
- Network sementation, All services are on one network in this implementation
- Backups for the Database
- Grafana auth, I used default admin/admin.
