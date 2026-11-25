# Mirdom Proxy

[![Release](https://img.shields.io/github/v/release/keysim86/ha-mirdom-proxy?style=flat-square)](https://github.com/keysim86/ha-mirdom-proxy/releases/latest)
[![HACS](https://img.shields.io/badge/HACS-Custom-orange.svg?style=flat-square)](https://github.com/keysim86/ha-mirdom-proxy)
[![HA](https://img.shields.io/badge/Home%20Assistant-2021.6%2B-blue?style=flat-square)](https://www.home-assistant.io/)
[![License](https://img.shields.io/github/license/keysim86/ha-mirdom-proxy.svg?style=flat-square)](LICENSE)

Custom component dla Home Assistant. Wystawia reverse proxy pod `/mirdom/` na serwerze HA, przekierowując ruch do lokalnie działającego [Mirdom Agent](https://forgejo.keynet.ovh/keysim/mirdom-agent).

Dzięki temu agent jest dostępny zarówno lokalnie, jak i przez tunel Cloudflare — bez osobnego wystawiania portu na zewnątrz. Dostęp chroniony własnym sekretem niezależnym od auth HA.

## Wymagania

- Home Assistant 2023.1+
- Działający [Mirdom Agent](https://forgejo.keynet.ovh/keysim/mirdom-agent) dostępny z hosta HA

## Instalacja przez HACS

1. HACS → **Custom repositories** → dodaj `https://forgejo.keynet.ovh/homelab/ha-mirdom-proxy` jako typ **Integration**
2. Znajdź **Mirdom Proxy** w HACS i zainstaluj
3. Zrestartuj Home Assistant

## Instalacja ręczna

Skopiuj folder `custom_components/mirdom_proxy/` do `<config>/custom_components/` i zrestartuj HA.

## Konfiguracja

**`configuration.yaml`:**
```yaml
mirdom_proxy:
  secret: !secret mirdom_proxy_secret
  agent_url: "http://localhost:8088"   # opcjonalne, to jest wartość domyślna
```

**`secrets.yaml`:**
```yaml
mirdom_proxy_secret: "twój-losowy-secret"
```

## Karta w dashboardzie

```yaml
type: webpage
url: /mirdom/?secret=twój-losowy-secret
```

Przy pierwszym otwarciu proxy ustawia sesję cookie (ważną 30 dni) i przekierowuje na `/mirdom/`. Kolejne wizyty nie wymagają `?secret` w URL — wystarczy cookie.

## Jak to działa

```
Przeglądarka → HA (Cloudflare tunnel) → /mirdom/* → localhost:8088
```

1. Karta ładuje `/mirdom/?secret=<SECRET>`
2. Komponent waliduje secret, ustawia cookie `mirdom_session`, redirect na `/mirdom/`
3. Strona agenta ładuje się; żądania AJAX (`fetch('chat', ...)`) idą do `/mirdom/chat` z cookie automatycznie
4. Proxy waliduje cookie i przekazuje ruch do `agent_url`
