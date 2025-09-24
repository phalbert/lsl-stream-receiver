# Quick Start Guide

## Installation

### 🚀 Quick Setup (Recommended)
```bash
git clone <repository-url>
cd lsl-stream-receiver
make setup          # Creates venv and installs everything
make app           # Starts the web application
```

### 📦 Manual Installation
1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd lsl-stream-receiver
   ```

2. **Create virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Verify installation**
   ```bash
   python -c "import pylsl; print('LSL installed successfully')"
   ```

## Basic Usage

### Option 1: Streamlit Web Interface (Recommended)

```bash
make app
# Open browser to http://localhost:8501
```

**Or manually:**
```bash
streamlit run streamlit_app/app.py
```

### Option 2: Python Script

```python
from lsl_receiver import StreamManager

# Create manager
manager = StreamManager()

# Discover and connect to streams
streams = manager.discover_streams()
manager.connect_to_streams(streams)

# Start receiving
manager.start_receiving()

# Monitor data
import time
for i in range(100):  # Run for 100 iterations
    data = manager.get_latest_data()
    print(f"Received data from {len(data)} streams")
    time.sleep(0.1)

# Clean up
manager.stop_receiving()
```

## Available Make Commands

| Command | Description |
|---------|-------------|
| `make setup` | Create virtual environment and install all dependencies |
| `make app` | Start the Streamlit web application |
| `make dev` | Start in development mode with hot reload |
| `make examples` | Run example scripts with interactive menu |
| `make test` | Run unit tests |
| `make lint` | Check code quality |
| `make format` | Format code with black |
| `make clean` | Remove temporary files |
| `make help` | Show all available commands |

## Lab-Specific Examples

### Physiological Data Collection

```python
from lsl_receiver import StreamManager, DataLogger

# Setup
logger = DataLogger(
    output_dir="physiology_data",
    session_name="participant_001_session_1",
    formats=['csv', 'json']
)

manager = StreamManager(target_streams=['EEG', 'EDA', 'PPG', 'ECG'])
manager.start_receiving(data_logger=logger)

# Run experiment...
# manager.stop_receiving() when done
```

### Multi-Device Synchronization

```python
from lsl_receiver import StreamManager, QualityAssessor

# Setup quality monitoring
assessor = QualityAssessor(check_interval=10.0)

# Connect to all available streams
manager = StreamManager()
streams = manager.discover_streams()
manager.connect_to_streams(streams)

# Start with quality monitoring
manager.start_receiving(quality_assessor=assessor)

# Monitor synchronization
while True:
    status = manager.get_status_summary()
    print(f"Streams: {status['connected_streams']}, "
          f"Samples: {status['total_samples_received']}")
    time.sleep(5)
```

## Configuration Options

### Stream Discovery

```python
# Connect to specific streams
manager = StreamManager(target_streams=['EEG', 'EyeTracking'])

# Auto-discover all streams (default)
manager = StreamManager(auto_discovery=True)
```

### Data Logging

```python
# CSV only (fastest)
logger = DataLogger(formats=['csv'])

# Multiple formats with metadata
logger = DataLogger(
    formats=['csv', 'json', 'parquet'],
    include_metadata=True,
    quality_metrics=True
)
```

### Quality Monitoring

```python
# Basic quality monitoring
assessor = QualityAssessor()

# Strict quality requirements
assessor = QualityAssessor(
    check_interval=10.0,                    # Check every 10 seconds
    required_sampling_rate_tolerance=0.05,  # 5% tolerance
    max_missing_data_ratio=0.05             # Max 5% missing data
)
```

## Output Files

Data is organized in session directories:

```
physiology_data/
└── participant_001_session_1/
    ├── lsl_data_20231201_143022.csv      # Main data
    ├── lsl_data_20231201_143022.json     # JSON format
    ├── session_metadata_20231201_143022.json # Metadata
    ├── session_summary_1701438222.json   # Summary
    └── events.jsonl                      # Event log
```

## Monitoring and Troubleshooting

### Check Available Streams

```python
from lsl_receiver import StreamManager

manager = StreamManager()
streams = manager.discover_streams()

print("Available streams:")
for name, info in streams.items():
    print(f"  - {name}: {info.type()} ({info.nominal_srate()} Hz)")
```

### Monitor Stream Status

```python
status = manager.get_status_summary()
print(f"Connected: {status['connected_streams']}")
print(f"Total samples: {status['total_samples_received']}")

for stream_name, info in status['stream_info'].items():
    print(f"{stream_name}: {info['samples_received']} samples")
```

### Common Issues

**No streams found:**
- Check that LSL devices are running
- Verify network connectivity
- Try `list_lsl_streams.py` to see available streams

**Connection drops:**
- Increase reconnection attempts
- Check network stability
- Monitor system resources

**High CPU usage:**
- Reduce monitoring frequency
- Increase buffer sizes
- Use CSV-only logging for large datasets

## Getting Help

1. **Check the examples**: `examples/` directory contains working code
2. **Read the documentation**: `docs/README.md` for detailed information
3. **Contact the lab tech team**: For device-specific issues
4. **Create an issue**: In this repository for bugs and feature requests
