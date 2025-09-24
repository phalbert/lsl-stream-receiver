# LSL Stream Receiver

A comprehensive, lab-ready solution for receiving and managing data from multiple LSL (Lab Streaming Layer) streams. This repository provides both a Python library and a Streamlit web interface for easy configuration and monitoring.

## Features

- **Multi-stream Support**: Receive data from multiple LSL streams simultaneously
- **Real-time Monitoring**: Live visualization of stream data and status
- **Flexible Logging**: Save data to CSV, JSON, or custom formats
- **Stream Management**: Automatic stream discovery, connection management, and reconnection
- **Data Quality**: Built-in signal quality assessment and metadata collection
- **Web Interface**: User-friendly Streamlit app for configuration and monitoring
- **Research Ready**: Comprehensive logging with timestamps, metadata, and quality metrics
- **Automated Setup**: Comprehensive Makefile for easy installation and development

## Quick Start

### 🚀 One-Command Setup (Recommended)

```bash
git clone <repository-url>
cd lsl-stream-receiver
make setup          # Creates venv and installs everything
make app           # Starts the Streamlit web application
```

### 📦 Manual Installation

```bash
git clone <repository-url>
cd lsl-stream-receiver
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 💻 Usage Options

**Option 1: Web Interface (Easiest)**
```bash
make app
# Open browser to http://localhost:8501
```

**Option 2: Python Script**
```python
from lsl_receiver import StreamManager

# Create stream manager
manager = StreamManager()

# Start receiving data
manager.start_receiving()

# Access latest data
for stream_name, stream_data in manager.get_latest_data().items():
    print(f"{stream_name}: {stream_data}")

# Stop receiving
manager.stop_receiving()
```

**Option 3: Interactive Examples**
```bash
make examples
# Select from menu of example scripts
```

### 📋 Available Make Commands

| Command | Description |
|---------|-------------|
| `make setup` | Create virtual environment and install dependencies |
| `make app` | Start the Streamlit web application |
| `make dev` | Start in development mode with hot reload |
| `make examples` | Run example scripts with interactive menu |
| `make test` | Run all tests |
| `make clean` | Clean up temporary files |
| `make lint` | Run code quality checks |
| `make format` | Format code with black |
| `make help` | Show all available commands |

## 🔧 Development & Automation

This repository includes a comprehensive Makefile that automates common development and usage tasks:

### Environment Setup
- **`make setup`**: Creates virtual environment and installs all dependencies
- **`make install`**: Updates dependencies in existing environment
- **`make venv-check`**: Verifies virtual environment setup

### Application Control
- **`make app`**: Start the Streamlit web application
- **`make dev`**: Start in development mode with hot reload
- **`make examples`**: Interactive menu to run example scripts

### Development Tools
- **`make test`**: Run unit tests
- **`make lint`**: Code quality checks (flake8, pylint)
- **`make format`**: Format code with black
- **`make clean`**: Remove temporary files
- **`make clean-all`**: Remove everything including virtual environment

### Documentation & Quality
- **`make docs`**: Generate documentation
- **`make health`**: Run system health check
- **`make status`**: Show project status

**Example workflow:**
```bash
git clone <repo>
cd lsl-stream-receiver
make setup          # Setup everything
make app           # Start the app
make examples      # Try examples
make clean         # Clean up
```

## Architecture

```
lsl-stream-receiver/
├── lsl_receiver/           # Core Python library
│   ├── __init__.py
│   ├── core.py            # Main receiver and stream management
│   ├── stream_manager.py  # Multi-stream coordination
│   └── utils.py           # Utility functions
├── streamlit_app/         # Web interface
│   ├── app.py            # Main Streamlit application
│   └── config.py         # Configuration management
├── examples/             # Usage examples
│   ├── basic_receiver.py
│   ├── csv_logger.py
│   └── real_time_plotter.py
├── docs/                # Documentation
│   ├── usage.md
│   └── api.md
└── tests/              # Unit tests
    ├── test_core.py
    └── test_integration.py
```

## Key Components

### StreamManager
- Discovers and connects to available LSL streams
- Manages multiple streams with different sampling rates
- Handles stream disconnections and reconnections
- Provides synchronized data access

### Data Logger
- Configurable output formats (CSV, JSON, HDF5)
- Comprehensive metadata collection
- Quality metrics and signal statistics
- Session-based organization

### Streamlit Interface
- Real-time stream monitoring
- Interactive configuration
- Data quality visualization
- Export and analysis tools

## Use Cases

### Research Data Collection
- Physiological signals (EEG, ECG, EDA, etc.)
- Behavioral data (eye tracking, motion capture)
- Environmental sensors (temperature, humidity)
- Experimental timing and events

### Lab Equipment Integration
- Multi-device synchronization
- Real-time data validation
- Automated logging and storage
- Quality control monitoring

### Development and Testing
- Stream simulation for testing
- Protocol validation
- Performance benchmarking
- Integration testing

## Configuration

### Stream Discovery
- Automatic discovery of all available LSL streams
- Manual specification of target streams
- Stream type and metadata validation

### Data Storage
- Configurable output directories
- Multiple format support
- Metadata inclusion options
- Quality metrics logging

### Quality Control
- Signal quality assessment
- Missing data detection
- Sampling rate validation
- Stream stability monitoring

## Contributing

We welcome contributions from lab members! Please see our [contributing guidelines](docs/contributing.md) for details.

## License

MIT License - see LICENSE file for details.

## Support

For questions or issues:
- Create an issue in this repository
- Contact the lab's technical support team
- Check the [documentation](docs/) for common solutions
