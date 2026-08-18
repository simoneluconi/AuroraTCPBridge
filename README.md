# AuroraTCPBridge

Native Home Assistant custom integration for Aurora/ABB/Power-One PV inverters connected via a TCP-to-serial gateway. No MQTT, no Docker add-on — it polls the inverter directly through [aurorapy](https://pypi.org/project/aurorapy/) inside a `DataUpdateCoordinator` and creates entities natively.

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=simoneluconi&repository=AuroraTCPBridge&category=integration)

## Features

- Config flow (GUI setup): host, port, inverter address, poll interval — with a live connection test.
- Sensors: output power, input voltage, input 1/2 current, daily/weekly/monthly/yearly/total energy, inverter temperature, status, last response timestamp.
- Binary sensor: `responding` (connectivity) — on when the inverter answers polls.
- Automatic reconnection with exponential backoff: after 3 consecutive failed polls the socket is closed and reconnected, backing off from the poll interval up to a 5 minute cap, resetting as soon as the inverter responds again. No more manual restarts when the inverter goes quiet overnight.

## Installation

### Via HACS (recommended)

1. Click the badge above, or in HACS go to **Integrations → ⋮ → Custom repositories** and add `https://github.com/simoneluconi/AuroraTCPBridge` as category **Integration**.
2. Install **AuroraTCPBridge** from HACS.
3. Restart Home Assistant.

### Manual

1. Copy `custom_components/aurora_tcp_bridge` into your Home Assistant `config/custom_components/` directory.
2. Restart Home Assistant.

## Configuration

Go to **Settings → Devices & Services → Add Integration**, search for **AuroraTCPBridge**, and enter:

| Field | Description | Default |
|---|---|---|
| Host | IP address of the TCP-to-serial gateway | — |
| Port | TCP port of the gateway | `8899` |
| Address | Aurora inverter RS485 address | `2` |
| Poll interval | Seconds between polls | `10` |

## License

[MIT](LICENSE)
