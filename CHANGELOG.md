# Changelog

## [1.0.0-beta.1] - 2026-05-29

### Added
- Reverse proxy `/mirdom/{path}` → skonfigurowany `agent_url` (domyślnie `http://localhost:8088`)
- Własna autentykacja: `?secret=<SECRET>` ustawia sesję cookie (30 dni, `httponly`, `SameSite=Lax`) i przekierowuje na `/mirdom/`; kolejne żądania z cookie nie wymagają secret w URL
- `requires_auth = False` — HA nie blokuje endpointu, komponent sam waliduje dostęp
- Konfiguracja przez `configuration.yaml`: `mirdom_proxy.secret` (wymagane) i `mirdom_proxy.agent_url` (opcjonalne)
