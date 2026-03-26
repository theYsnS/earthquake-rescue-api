# Earthquake Rescue Coordination System

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)](https://fastapi.tiangolo.com)
[![Docker](https://img.shields.io/badge/Docker-Compose-blue.svg)](https://docker.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Backend API and IoT integration system for earthquake rescue coordination. Developed as part of a TUBITAK-supported research project to improve post-disaster communication, team coordination, and rescue operations through technology.

## Features

- **Rescue Reports**: GPS-based distress reporting with severity classification
- **Team Management**: Real-time tracking and assignment of rescue teams
- **IoT Integration**: MQTT-based sensor data collection (vibration, gas, sound)
- **Auto-coordination**: Nearest-team assignment with priority scoring
- **Notifications**: Priority-based alert routing for rescue operations
- **Geospatial Queries**: Find nearby reports using Haversine distance

## Architecture

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│ Mobile App   │────▶│   FastAPI    │────▶│  SQLite DB   │
│ (Reports)    │     │   Server     │     │              │
└──────────────┘     └──────┬───────┘     └──────────────┘
                            │
┌──────────────┐     ┌──────▼───────┐     ┌──────────────┐
│ IoT Sensors  │────▶│ MQTT Handler │────▶│ Coordinator  │
│ (ESP32/RPi)  │     │ (Mosquitto)  │     │ (Auto-assign)│
└──────────────┘     └──────────────┘     └──────────────┘
                            │
                     ┌──────▼───────┐
                     │ Notification │
                     │  Service     │
                     └──────────────┘
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/rescue/report` | Submit rescue report |
| GET | `/rescue/reports` | List reports with filters |
| PUT | `/rescue/reports/{id}/status` | Update rescue status |
| GET | `/rescue/reports/nearby` | Find nearby reports |
| GET | `/rescue/stats` | Dashboard statistics |
| POST | `/teams` | Register rescue team |
| GET | `/teams` | List active teams |
| PUT | `/teams/{id}/location` | Update team GPS |
| POST | `/teams/{id}/assign` | Assign team to report |
| POST | `/devices/register` | Register IoT sensor |
| POST | `/devices/{id}/data` | Submit sensor data |

## Installation

```bash
git clone https://github.com/theYsnS/earthquake-rescue-api.git
cd earthquake-rescue-api
pip install -r requirements.txt
```

### Docker

```bash
docker-compose up -d
```

## Usage

```bash
# Start API server
python main.py

# API documentation
# http://localhost:8000/docs
```

## License

MIT License - see [LICENSE](LICENSE) for details.
