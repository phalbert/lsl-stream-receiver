# LSL Stream Receiver Documentation

## Overview

The LSL Stream Receiver is a comprehensive, lab-ready solution for receiving and managing data from multiple LSL (Lab Streaming Layer) streams. This system provides both a Python library for programmatic access and a Streamlit web interface for easy configuration and monitoring.

## Features

- **Multi-stream Support**: Receive data from multiple LSL streams simultaneously
- **Real-time Monitoring**: Live visualization of stream data and status
- **Flexible Logging**: Save data to CSV, JSON, Parquet, or custom formats
- **Quality Monitoring**: Built-in signal quality assessment and validation
- **Web Interface**: User-friendly Streamlit app for configuration and monitoring
- **Research Ready**: Comprehensive logging with timestamps, metadata, and quality metrics

## Quick Start

### Installation

```bash
git clone <repository-url>
cd lsl-stream-receiver
pip install -r requirements.txt
```

### Basic Usage

```python
from lsl_receiver import StreamManager

# Create and configure stream manager
manager = StreamManager()

# Discover and connect to available streams
stream_infos = manager.discover_streams()
manager.connect_to_streams(stream_infos)

# Start receiving data
manager.start_receiving()

# Access latest data
latest_data = manager.get_latest_data()

# Stop receiving
manager.stop_receiving()
```

### Streamlit App

```bash
streamlit run streamlit_app/app.py
```

## Architecture

```
lsl-stream-receiver/
├── lsl_receiver/           # Core Python library
│   ├── __init__.py        # Package initialization
│   ├── core.py            # StreamManager and StreamReceiver
│   ├── data_logger.py     # Data logging functionality
│   └── quality_assessor.py # Quality assessment
├── streamlit_app/         # Web interface
│   ├── app.py             # Main Streamlit application
│   └── config.py          # Configuration management
├── examples/              # Usage examples
│   ├── basic_receiver.py  # Simple data reception
│   ├── csv_logger.py      # CSV logging example
│   └── real_time_plotter.py # Real-time plotting
├── docs/                  # Documentation
│   ├── README.md          # This file
│   ├── api.md             # API reference
│   └── examples.md        # Detailed examples
└── tests/                 # Unit tests
```

## Core Components

### StreamManager

The `StreamManager` class is the main interface for managing multiple LSL streams:

```python
from lsl_receiver import StreamManager

manager = StreamManager(
    target_streams=['EEG', 'Physiological'],  # Optional: specific streams
    auto_discovery=True,                       # Auto-discover streams
    reconnect_attempts=3                       # Reconnection attempts
)

# Start receiving
manager.start_receiving()

# Get data
data = manager.get_latest_data()
status = manager.get_status_summary()

# Stop
manager.stop_receiving()
```

### DataLogger

The `DataLogger` class handles saving data to various formats:

```python
from lsl_receiver import DataLogger

logger = DataLogger(
    output_dir="my_data",
    formats=['csv', 'json'],     # Output formats
    session_name="experiment_1", # Session identifier
    include_metadata=True,       # Include comprehensive metadata
    quality_metrics=True         # Compute quality metrics
)

# Log samples
logger.log_samples(sample_data)

# Save session summary
logger.save_session_summary()
logger.close()
```

### QualityAssessor

The `QualityAssessor` monitors signal quality:

```python
from lsl_receiver import QualityAssessor

assessor = QualityAssessor(
    check_interval=30.0,                    # Check every 30 seconds
    required_sampling_rate_tolerance=0.1,   # 10% tolerance
    max_missing_data_ratio=0.1              # Max 10% missing data
)

# Assess quality
stream_infos = manager.get_stream_info()
quality_report = assessor.assess_quality(stream_infos)
```

## Streamlit Web Interface

The Streamlit app provides a user-friendly interface for:

- **Stream Discovery**: Automatically find available LSL streams
- **Real-time Monitoring**: Live visualization of stream data
- **Data Export**: Download collected data in various formats
- **Quality Assessment**: Monitor signal quality metrics
- **Session Management**: Organize data collection sessions

### Running the App

```bash
streamlit run streamlit_app/app.py
```

### Features

- **Dashboard**: Overview of connected streams and data statistics
- **Stream Details**: Detailed information about each stream
- **Data Management**: Export and manage collected data
- **Settings**: Configure logging and quality parameters
- **Real-time Plots**: Live visualization of stream data

## Examples

### Basic Data Reception

```python
from lsl_receiver import StreamManager

# Simple data collection
manager = StreamManager()
manager.connect_to_streams(manager.discover_streams())
manager.start_receiving()

while True:
    data = manager.get_latest_data()
    # Process data...
```

### CSV Logging

```python
from lsl_receiver import StreamManager, DataLogger

# Setup logging
logger = DataLogger(
    output_dir="experiment_data",
    formats=['csv', 'json'],
    session_name="my_experiment"
)

# Receive with logging
manager = StreamManager()
manager.start_receiving(data_logger=logger)
```

### Quality Monitoring

```python
from lsl_receiver import StreamManager, QualityAssessor

# Setup quality monitoring
assessor = QualityAssessor(check_interval=10.0)
manager = StreamManager()

# Monitor quality
while True:
    quality_report = assessor.assess_quality(manager.get_stream_info())
    print(f"Overall quality: {quality_report['overall_quality']}")
```

## Configuration

### Stream Discovery

- **Automatic**: Discover all available LSL streams
- **Targeted**: Connect to specific streams by name
- **Type-based**: Filter streams by type (EEG, Physiological, etc.)

### Data Storage

- **Formats**: CSV, JSON, Parquet, HDF5
- **Organization**: Session-based directory structure
- **Metadata**: Comprehensive logging of experimental conditions

### Quality Control

- **Sampling Rate**: Monitor for deviations from nominal rates
- **Missing Data**: Detect gaps in data streams
- **Connection Stability**: Track reconnection attempts and errors

## Use Cases

### Research Data Collection

```python
# Collect physiological data from multiple sensors
manager = StreamManager(target_streams=['EEG', 'ECG', 'EDA', 'EyeTracking'])
logger = DataLogger(session_name="physiology_study_session_1")
manager.start_receiving(data_logger=logger)
```

### Lab Equipment Integration

```python
# Integrate with lab equipment
streams = manager.discover_streams()
manager.connect_to_streams(streams)
manager.start_receiving()

# Monitor equipment status
status = manager.get_status_summary()
for stream_name, info in status['stream_info'].items():
    print(f"{stream_name}: {info['samples_received']} samples")
```

### Development and Testing

```python
# Test stream connections
manager = StreamManager()
streams = manager.discover_streams()

for name, info in streams.items():
    print(f"Found: {name} ({info.type()}, {info.nominal_srate()} Hz)")
```

## API Reference

### StreamManager

- `discover_streams() -> Dict[str, StreamInfo]`: Discover available streams
- `connect_to_streams(stream_infos: Dict) -> bool`: Connect to specified streams
- `start_receiving(data_logger=None, quality_assessor=None) -> bool`: Start data reception
- `stop_receiving()`: Stop data reception
- `get_latest_data(stream_name=None, n_samples=10) -> Dict`: Get recent data
- `get_stream_info(stream_name=None) -> Dict`: Get stream information
- `get_status_summary() -> Dict`: Get comprehensive status

### DataLogger

- `log_samples(samples: List[Dict])`: Log sample data
- `save_session_summary()`: Save comprehensive session summary
- `close()`: Close file handles and finalize session

### QualityAssessor

- `assess_quality(stream_infos: Dict) -> Dict`: Assess stream quality
- `get_quality_history(stream_name=None) -> Dict`: Get quality history

## Best Practices

### Stream Management

1. **Always handle disconnections**: Use the built-in reconnection logic
2. **Monitor sampling rates**: Check for deviations from nominal rates
3. **Use appropriate buffer sizes**: Balance memory usage with data availability

### Data Logging

1. **Choose appropriate formats**: CSV for analysis, JSON for metadata
2. **Include session metadata**: Record experimental conditions
3. **Monitor disk space**: Large experiments may generate significant data

### Quality Control

1. **Set appropriate thresholds**: Adjust for your specific requirements
2. **Regular monitoring**: Check quality throughout experiments
3. **Log quality metrics**: Use for post-experiment analysis

## Troubleshooting

### Common Issues

**No streams found**
- Check that LSL devices are running and streaming
- Verify network connectivity
- Ensure streams are being published to the correct network interface

**Connection drops**
- Increase reconnection attempts
- Check network stability
- Monitor system resources

**Missing data**
- Verify stream configuration
- Check for device-specific issues
- Review sampling rate settings

### Performance Optimization

**High CPU usage**
- Reduce update frequency in monitoring applications
- Increase buffer sizes to reduce system calls
- Use appropriate logging intervals

**Memory usage**
- Set reasonable buffer sizes
- Use streaming data formats for large datasets
- Monitor and clean up old data

**Disk space**
- Use compressed formats (Parquet) for large datasets
- Implement data rotation policies
- Monitor available storage space

## Contributing

We welcome contributions from lab members! Please see our contributing guidelines for details on:

- Code style and standards
- Testing requirements
- Documentation updates
- Pull request process

## Support

For questions or issues:
1. Check the troubleshooting section above
2. Review the example code
3. Contact the lab's technical support team
4. Create an issue in this repository

## License

This project is licensed under the MIT License - see the LICENSE file for details.

---

*This documentation is maintained by the lab's technical team. Last updated: $(date)*
