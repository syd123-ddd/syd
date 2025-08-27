# aMon - Kubernetes & Jenkins Monitoring

aMon is a Django-based monitoring application that provides a unified interface for monitoring Kubernetes logs via Loki and Jenkins pipeline status.

## Features

- Kubernetes log monitoring using Loki
- Jenkins pipeline status monitoring
- Real-time updates for Jenkins jobs
- Customizable log queries
- Time-range selection for logs
- Modern, responsive UI
- RESTful API endpoints
- WebSocket support for real-time updates
- Customizable dashboard layouts
- Export functionality for logs and metrics


## Installation

1. Clone the repository:
```bash
cd aMon
```

2. Create and activate a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate
```

3. Install dependencies:
```bash
python3 -m venv venv
pip install -r requirements.txt
```

4. Start the development server:
```bash
# Option 1: Using run.sh script
./run.sh

# Option 2: Manual start
python3 manage.py runserver
```

## Usage

`http://localhost:8000`