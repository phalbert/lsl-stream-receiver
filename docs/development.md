# LSL Stream Receiver Development Guide

This guide provides comprehensive information for developers working with the LSL Stream Receiver codebase, including API reference, architecture details, and development setup instructions.

## 📋 Table of Contents

- [Development Environment](#-development-environment)
- [Architecture Overview](#-architecture-overview)
- [API Reference](#-api-reference)
- [Core Components](#-core-components)
- [Advanced Usage](#-advanced-usage)
- [Testing Strategy](#-testing-strategy)
- [Performance Optimization](#-performance-optimization)
- [Debugging and Profiling](#-debugging-and-profiling)

## 🛠️ Development Environment

### Prerequisites

- **Python 3.8+** with pip and venv support
- **Git** for version control
- **GitHub account** for pull requests
- **Basic understanding** of LSL (Lab Streaming Layer)
- **Optional**: Docker for containerized development

### Setup Instructions

1. **Fork and clone the repository**:
   ```bash
   git clone https://github.com/your-username/lsl-stream-receiver.git
   cd lsl-stream-receiver
   ```

2. **Create development environment**:
   ```bash
   make setup          # Creates venv and installs dependencies
   make dev-setup      # Installs development tools
   ```

3. **Verify installation**:
   ```bash
   make health         # Run health checks
   make test           # Run test suite
   make lint           # Check code quality
   ```

### Development Tools

The Makefile provides comprehensive development automation:

```bash
# Development workflow
make dev            # Start development server with hot reload
make test           # Run tests with coverage
make lint           # Run flake8 and pylint
make format         # Format code with black
make docs           # Generate documentation
make clean          # Clean temporary files
```

### Project Structure

```
lsl-stream-receiver/
├── lsl_receiver/           # Core Python library
│   ├── __init__.py        # Package initialization
│   ├── core.py            # StreamManager and StreamReceiver
│   ├── data_logger.py     # Data logging functionality
│   ├── quality_assessor.py # Quality assessment
│   ├── testing/           # Testing utilities
│   └── utils.py           # Utility functions
├── streamlit_app/         # Web interface
│   ├── app.py            # Main Streamlit application
│   └── config.py         # Configuration management
├── examples/             # Usage examples
│   ├── basic_receiver.py # Simple data reception
│   ├── csv_logger.py     # CSV logging example
│   ├── real_time_plotter.py # Real-time plotting
│   └── lab_study_collector.py # Complete workflow
├── docs/                # Documentation
│   ├── README.md        # Technical documentation
│   ├── user_guide.md    # User guide
│   ├── development.md   # This file
│   ├── architecture.md  # Architecture details
│   └── contributing.md  # Contributing guidelines
├── tests/              # Test suite
│   ├── test_core.py
│   ├── test_integration.py
│   ├── test_data_logger.py
│   └── test_quality_assessor.py
├── requirements.txt    # Runtime dependencies
├── requirements-dev.txt # Development dependencies
├── Makefile           # Development automation
└── pyproject.toml     # Python project configuration
```

## 🏗️ Architecture Overview

### System Design Principles

The LSL Stream Receiver follows these key architectural principles:

- **Modular Design**: Separated concerns with clear interfaces
- **Thread Safety**: Concurrent stream handling with proper synchronization
- **Extensibility**: Plugin architecture for new stream types and formats
- **Quality First**: Built-in quality assessment and validation
- **Performance**: Optimized for real-time data processing

### Component Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   StreamManager │───▶│  Data Logger    │    │ Quality Assessor│
│                 │    │                 │    │                 │
│ - Stream discovery   │ - Multiple formats   │ - Quality metrics   │
│ - Connection mgmt    │ - Metadata handling  │ - Real-time monitoring│
│ - Data buffering     │ - Session mgmt       │ - Alert system      │
│ - Synchronization    │ - Export tools       │ - Historical data   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │ Streamlit App   │
                    │                 │
                    │ - Web interface │
                    │ - Real-time viz │
                    │ - Configuration  │
                    │ - Data export    │
                    └─────────────────┘
```

### Data Flow Architecture

1. **Stream Discovery**: LSL stream resolution and metadata collection
2. **Connection Management**: Establishing and maintaining stream connections
3. **Data Reception**: Continuous data acquisition from connected streams
4. **Quality Assessment**: Real-time quality monitoring and validation
5. **Data Processing**: Buffering, synchronization, and preprocessing
6. **Storage**: Multiple format export with comprehensive metadata
7. **Visualization**: Real-time display and monitoring interfaces

## 📚 API Reference

### StreamManager

The main interface for managing multiple LSL streams:

```python
from lsl_receiver import StreamManager
from typing import Dict, List, Optional, Any

class StreamManager:
    """Manages multiple LSL streams with synchronized data reception.

    This class provides the main interface for discovering, connecting to,
    and receiving data from multiple Lab Streaming Layer streams. It handles
    stream reconnection, data buffering, and quality monitoring.

    Args:
        target_streams: List of specific stream names to connect to
        auto_discovery: Whether to auto-discover available streams
        reconnect_attempts: Number of reconnection attempts on failure
        buffer_size: Size of data buffer for each stream
        update_interval: Frequency of data updates (seconds)
        sync_streams: Whether to synchronize streams temporally

    Attributes:
        streams: Dictionary of connected stream inlets
        is_running: Whether data reception is active
        stream_info: Metadata for connected streams
        buffer_size: Size of data buffer for each stream
    """

    def __init__(
        self,
        target_streams: Optional[List[str]] = None,
        auto_discovery: bool = True,
        reconnect_attempts: int = 3,
        buffer_size: int = 1000,
        update_interval: float = 0.05,
        sync_streams: bool = False
    ) -> None:
        """Initialize StreamManager with specified configuration."""

    def discover_streams(self) -> Dict[str, Any]:
        """Discover available LSL streams.

        Returns:
            Dictionary mapping stream names to StreamInfo objects

        Raises:
            RuntimeError: If stream discovery fails
        """

    def connect_to_streams(self, stream_infos: Dict[str, Any]) -> bool:
        """Connect to specified streams.

        Args:
            stream_infos: Dictionary of stream information

        Returns:
            True if all connections successful, False otherwise
        """

    def start_receiving(
        self,
        data_logger: Optional[Any] = None,
        quality_assessor: Optional[Any] = None
    ) -> bool:
        """Start receiving data from connected streams.

        Args:
            data_logger: Optional DataLogger instance
            quality_assessor: Optional QualityAssessor instance

        Returns:
            True if started successfully, False otherwise

        Raises:
            RuntimeError: If already running or no streams connected
        """

    def stop_receiving(self) -> None:
        """Stop data reception and close connections."""

    def get_latest_data(
        self,
        stream_name: Optional[str] = None,
        n_samples: int = 10
    ) -> Dict[str, Any]:
        """Get recent data from streams.

        Args:
            stream_name: Specific stream name (None for all)
            n_samples: Number of recent samples to return

        Returns:
            Dictionary mapping stream names to data arrays
        """

    def get_stream_info(self, stream_name: Optional[str] = None) -> Dict[str, Any]:
        """Get stream information and metadata.

        Args:
            stream_name: Specific stream name (None for all)

        Returns:
            Dictionary with stream metadata and status
        """

    def get_status_summary(self) -> Dict[str, Any]:
        """Get comprehensive status summary.

        Returns:
            Dictionary with overall status, stream info, and metrics
        """

    def disconnect_stream(self, stream_name: str) -> bool:
        """Disconnect a specific stream.

        Args:
            stream_name: Name of stream to disconnect

        Returns:
            True if disconnected successfully, False otherwise
        """
```

### DataLogger

Handles data logging to multiple formats with comprehensive metadata:

```python
from lsl_receiver import DataLogger
from typing import List, Dict, Optional, Any

class DataLogger:
    """Handles data logging to various formats with metadata.

    This class manages the logging of stream data to multiple output formats,
    including comprehensive metadata collection and session management.

    Args:
        output_dir: Directory for output files
        formats: List of output formats ('csv', 'json', 'parquet', 'hdf5')
        session_name: Identifier for the logging session
        include_metadata: Whether to include comprehensive metadata
        quality_metrics: Whether to compute and log quality metrics
        auto_save_interval: Auto-save interval in seconds
        compression: Compression method for supported formats

    Attributes:
        session_name: Current session identifier
        output_dir: Output directory path
        formats: Enabled output formats
        metadata: Session metadata dictionary
    """

    def __init__(
        self,
        output_dir: str = "lsl_data",
        formats: List[str] = ['csv', 'json'],
        session_name: Optional[str] = None,
        include_metadata: bool = True,
        quality_metrics: bool = True,
        auto_save_interval: float = 300.0,
        compression: Optional[str] = None
    ) -> None:
        """Initialize DataLogger with specified configuration."""

    def log_samples(self, samples: Dict[str, Any]) -> None:
        """Log sample data to all configured formats.

        Args:
            samples: Dictionary mapping stream names to data samples
        """

    def add_metadata(self, key: str, value: Any) -> None:
        """Add metadata entry to the session.

        Args:
            key: Metadata key
            value: Metadata value
        """

    def save_session_summary(self) -> None:
        """Save comprehensive session summary with metadata."""

    def export_session_data(self, format_type: str = 'all') -> None:
        """Export all logged data to specified format.

        Args:
            format_type: Format to export ('csv', 'json', 'parquet', 'all')
        """

    def clear_buffers(self) -> None:
        """Clear data buffers and reset session."""

    def close(self) -> None:
        """Close file handles and finalize session."""
```

### QualityAssessor

Monitors and assesses data stream quality in real-time:

```python
from lsl_receiver import QualityAssessor
from typing import Dict, Optional, Any

class QualityAssessor:
    """Assesses and monitors data stream quality.

    This class provides comprehensive quality assessment for LSL streams,
    including sampling rate monitoring, connection stability, and data
    integrity checks.

    Args:
        check_interval: Interval between quality checks (seconds)
        required_sampling_rate_tolerance: Allowed deviation from nominal rate
        max_missing_data_ratio: Maximum allowed missing data ratio
        min_connection_stability: Minimum required connection stability
        quality_history_length: Number of quality checks to retain

    Attributes:
        quality_history: History of quality assessments
        current_quality: Most recent quality assessment
        alert_thresholds: Thresholds for quality alerts
    """

    def __init__(
        self,
        check_interval: float = 30.0,
        required_sampling_rate_tolerance: float = 0.1,
        max_missing_data_ratio: float = 0.1,
        min_connection_stability: float = 0.95,
        quality_history_length: int = 100
    ) -> None:
        """Initialize QualityAssessor with specified parameters."""

    def assess_quality(self, stream_infos: Dict[str, Any]) -> Dict[str, Any]:
        """Assess quality of connected streams.

        Args:
            stream_infos: Dictionary of stream information

        Returns:
            Dictionary with quality metrics and assessment
        """

    def get_quality_history(
        self,
        stream_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get quality history for streams.

        Args:
            stream_name: Specific stream name (None for all)

        Returns:
            Dictionary with quality history data
        """

    def set_alert_thresholds(
        self,
        thresholds: Dict[str, float]
    ) -> None:
        """Set custom alert thresholds.

        Args:
            thresholds: Dictionary of threshold values
        """

    def get_alert_status(self) -> Dict[str, Any]:
        """Get current alert status.

        Returns:
            Dictionary with active alerts and status
        """
```

## 🔧 Core Components

### StreamReceiver

Handles individual stream connections and data reception:

```python
from lsl_receiver.core import StreamReceiver
from typing import Optional, Any, Callable

class StreamReceiver:
    """Handles data reception from a single LSL stream.

    This class manages the connection to a single LSL stream, handles
    data buffering, and provides quality monitoring for the stream.

    Args:
        stream_info: LSL StreamInfo object
        buffer_size: Size of data buffer
        reconnect_attempts: Number of reconnection attempts
        data_callback: Optional callback for received data

    Attributes:
        stream_name: Name of the connected stream
        is_connected: Whether stream is currently connected
        samples_received: Total samples received
        last_sample_time: Timestamp of last received sample
    """

    def __init__(
        self,
        stream_info: Any,
        buffer_size: int = 1000,
        reconnect_attempts: int = 3,
        data_callback: Optional[Callable] = None
    ) -> None:
        """Initialize StreamReceiver for specified stream."""

    def connect(self) -> bool:
        """Connect to the LSL stream.

        Returns:
            True if connection successful, False otherwise
        """

    def start_receiving(self) -> bool:
        """Start data reception from the stream.

        Returns:
            True if started successfully, False otherwise
        """

    def get_data(
        self,
        n_samples: int = 10,
        timeout: float = 1.0
    ) -> Optional[Any]:
        """Get recent data from the stream.

        Args:
            n_samples: Number of samples to return
            timeout: Timeout for data retrieval

        Returns:
            Data array or None if no data available
        """

    def get_quality_metrics(self) -> Dict[str, float]:
        """Get quality metrics for the stream.

        Returns:
            Dictionary with quality metrics
        """

    def disconnect(self) -> None:
        """Disconnect from the stream."""
```

### Synchronization Module

Handles temporal synchronization across multiple streams:

```python
from lsl_receiver.utils import StreamSynchronizer
from typing import Dict, List, Any

class StreamSynchronizer:
    """Synchronizes data from multiple streams temporally.

    This utility class handles temporal alignment of data from multiple
    streams with different sampling rates and latencies.

    Args:
        streams: Dictionary of stream information
        max_offset: Maximum allowed temporal offset (seconds)
        interpolation_method: Method for temporal interpolation

    Attributes:
        reference_stream: Name of reference stream for synchronization
        sync_offsets: Calculated synchronization offsets
        interpolation_method: Current interpolation method
    """

    def __init__(
        self,
        streams: Dict[str, Any],
        max_offset: float = 0.001,  # 1ms max offset
        interpolation_method: str = 'linear'
    ) -> None:
        """Initialize StreamSynchronizer with stream information."""

    def calculate_offsets(self) -> Dict[str, float]:
        """Calculate temporal offsets for all streams.

        Returns:
            Dictionary mapping stream names to offset values
        """

    def synchronize_data(
        self,
        data_dict: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Synchronize data from multiple streams.

        Args:
            data_dict: Dictionary mapping stream names to data

        Returns:
            Dictionary with synchronized data
        """

    def get_sync_status(self) -> Dict[str, Any]:
        """Get synchronization status and metrics.

        Returns:
            Dictionary with synchronization metrics
        """
```

## 🚀 Advanced Usage

### Custom Stream Processing

```python
from lsl_receiver import StreamManager
from scipy import signal
import numpy as np

class CustomProcessor:
    """Custom stream data processor."""

    def __init__(self, filter_type: str = 'bandpass', cutoff: tuple = (1, 40)):
        self.filter_type = filter_type
        self.cutoff = cutoff

    def process_eeg(self, data: np.ndarray, srate: float) -> np.ndarray:
        """Apply custom processing to EEG data."""
        if self.filter_type == 'bandpass':
            # Design bandpass filter
            nyquist = srate / 2
            low = self.cutoff[0] / nyquist
            high = self.cutoff[1] / nyquist
            b, a = signal.butter(4, [low, high], btype='band')

            # Apply filter
            return signal.filtfilt(b, a, data, axis=0)

        return data

# Use custom processor
processor = CustomProcessor(filter_type='bandpass', cutoff=(1, 40))
manager = StreamManager()

def process_data(data):
    """Custom data processing function."""
    processed = {}
    for stream_name, stream_data in data.items():
        if stream_name == 'EEG':
            processed[stream_name] = processor.process_eeg(stream_data, 500)
        else:
            processed[stream_name] = stream_data
    return processed

manager.start_receiving()
```

### Event-Driven Architecture

```python
from lsl_receiver import StreamManager
import asyncio
from typing import Callable, Any

class EventDrivenReceiver:
    """Event-driven stream data receiver."""

    def __init__(self, manager: StreamManager):
        self.manager = manager
        self.event_handlers = {}

    def register_handler(
        self,
        stream_name: str,
        handler: Callable[[Any], None]
    ) -> None:
        """Register event handler for stream data."""
        self.event_handlers[stream_name] = handler

    async def start_event_loop(self) -> None:
        """Start event-driven data processing."""
        self.manager.start_receiving()

        while True:
            data = self.manager.get_latest_data()

            for stream_name, stream_data in data.items():
                if stream_name in self.event_handlers:
                    await self.event_handlers[stream_name](stream_data)

            await asyncio.sleep(0.01)  # 10ms polling interval

# Usage example
manager = StreamManager()
receiver = EventDrivenReceiver(manager)

async def eeg_handler(data):
    """Handle EEG data events."""
    # Process EEG data
    if len(data) > 100:  # Detect artifacts
        print(f"Potential artifact detected in EEG data")

receiver.register_handler('EEG', eeg_handler)
receiver.register_handler('ECG', lambda d: print(f"ECG data: {d.shape}"))

# Run event loop
# asyncio.run(receiver.start_event_loop())
```

### Multi-threaded Processing

```python
from lsl_receiver import StreamManager
import threading
import queue
from typing import Dict, Any

class MultiThreadedReceiver:
    """Multi-threaded stream data receiver."""

    def __init__(self, manager: StreamManager):
        self.manager = manager
        self.data_queue = queue.Queue()
        self.processing_thread = None
        self.is_running = False

    def start(self) -> None:
        """Start multi-threaded data reception."""
        self.is_running = True
        self.manager.start_receiving()

        # Start processing thread
        self.processing_thread = threading.Thread(
            target=self._process_data,
            daemon=True
        )
        self.processing_thread.start()

    def _process_data(self) -> None:
        """Background data processing."""
        while self.is_running:
            data = self.manager.get_latest_data()
            if data:
                self.data_queue.put(data)
            threading.Event().wait(0.01)  # 10ms wait

    def get_processed_data(self, timeout: float = 1.0) -> Dict[str, Any]:
        """Get processed data from queue."""
        try:
            return self.data_queue.get(timeout=timeout)
        except queue.Empty:
            return {}

    def stop(self) -> None:
        """Stop multi-threaded processing."""
        self.is_running = False
        self.manager.stop_receiving()

        if self.processing_thread:
            self.processing_thread.join(timeout=1.0)

# Usage
manager = StreamManager()
receiver = MultiThreadedReceiver(manager)
receiver.start()

# In main thread
while True:
    data = receiver.get_processed_data()
    if data:
        # Process data in main thread
        process_data(data)
```

## 🧪 Testing Strategy

### Unit Testing

```python
import pytest
import numpy as np
from unittest.mock import Mock, patch
from lsl_receiver import StreamManager, DataLogger

class TestStreamManager:
    """Comprehensive unit tests for StreamManager."""

    def setup_method(self):
        """Set up test fixtures."""
        self.manager = StreamManager()
        self.mock_stream_info = Mock()
        self.mock_stream_info.name.return_value = 'TestStream'
        self.mock_stream_info.type.return_value = 'EEG'
        self.mock_stream_info.nominal_srate.return_value = 500.0

    def test_initialization(self):
        """Test StreamManager initialization."""
        assert self.manager.is_running is False
        assert self.manager.streams == {}
        assert self.manager.buffer_size == 1000

    def test_stream_discovery(self):
        """Test stream discovery functionality."""
        with patch('pylsl.resolve_streams') as mock_resolve:
            mock_resolve.return_value = [self.mock_stream_info]

            streams = self.manager.discover_streams()

            assert len(streams) == 1
            assert 'TestStream' in streams
            mock_resolve.assert_called_once()

    def test_invalid_sampling_rate(self):
        """Test error handling for invalid sampling rates."""
        with pytest.raises(ValueError, match="Sampling rate must be positive"):
            self.manager._validate_sampling_rate(-1.0)

    @pytest.mark.parametrize("n_samples", [1, 10, 100])
    def test_buffer_sizes(self, n_samples):
        """Test different buffer sizes."""
        manager = StreamManager(buffer_size=n_samples)
        assert manager.buffer_size == n_samples

    def test_connection_management(self):
        """Test stream connection and disconnection."""
        with patch.object(self.manager, 'connect_to_streams') as mock_connect:
            mock_connect.return_value = True

            result = self.manager.connect_to_streams({'test': self.mock_stream_info})

            assert result is True
            mock_connect.assert_called_once()
```

### Integration Testing

```python
import pytest
from lsl_receiver import StreamManager, DataLogger, QualityAssessor
import tempfile
import os

class TestIntegration:
    """Integration tests for complete workflows."""

    def setup_method(self):
        """Set up integration test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.logger = DataLogger(
            output_dir=self.temp_dir,
            formats=['csv', 'json'],
            session_name='test_session'
        )
        self.assessor = QualityAssessor(check_interval=1.0)
        self.manager = StreamManager()

    def teardown_method(self):
        """Clean up test fixtures."""
        self.logger.close()
        # Clean up temporary files

    def test_complete_workflow(self):
        """Test complete data collection workflow."""
        # Setup
        stream_infos = self.manager.discover_streams()
        if stream_infos:
            # Connect and start
            self.manager.connect_to_streams(stream_infos)
            self.manager.start_receiving(
                data_logger=self.logger,
                quality_assessor=self.assessor
            )

            # Collect data for a short period
            import time
            time.sleep(2.0)

            # Verify data collection
            data = self.manager.get_latest_data()
            assert isinstance(data, dict)

            # Check logging
            assert os.path.exists(self.temp_dir)

            # Stop
            self.manager.stop_receiving()

    def test_quality_assessment_integration(self):
        """Test quality assessment with real streams."""
        stream_infos = self.manager.discover_streams()

        if stream_infos:
            self.manager.connect_to_streams(stream_infos)
            self.manager.start_receiving()

            # Assess quality
            quality = self.assessor.assess_quality(self.manager.get_stream_info())

            assert 'overall_quality' in quality
            assert 'streams' in quality
            assert isinstance(quality['overall_quality'], float)

            self.manager.stop_receiving()

    def test_data_export_formats(self):
        """Test data export in multiple formats."""
        # Generate test data
        test_data = {
            'EEG': np.random.randn(100, 32),
            'ECG': np.random.randn(100, 3)
        }

        # Log test data
        for i in range(10):
            self.logger.log_samples(test_data)

        # Export data
        self.logger.export_session_data('csv')
        self.logger.export_session_data('json')

        # Verify exports
        assert os.path.exists(os.path.join(self.temp_dir, 'EEG.csv'))
        assert os.path.exists(os.path.join(self.temp_dir, 'ECG.csv'))
        assert os.path.exists(os.path.join(self.temp_dir, 'session_data.json'))
```

### Performance Testing

```python
import time
import psutil
import pytest
from lsl_receiver import StreamManager

class TestPerformance:
    """Performance tests for StreamManager."""

    def test_high_frequency_stream_handling(self):
        """Test handling of high-frequency streams."""
        manager = StreamManager(buffer_size=5000)

        # Simulate high-frequency data
        start_time = time.time()
        samples_processed = 0

        while time.time() - start_time < 10.0:  # Test for 10 seconds
            # Simulate processing 1000 samples
            data = np.random.randn(1000, 32)
            samples_processed += 1000

            # Short pause to simulate real processing
            time.sleep(0.001)

        throughput = samples_processed / (time.time() - start_time)
        assert throughput > 50000  # Should handle >50k samples/sec

    def test_memory_usage(self):
        """Test memory usage with large data buffers."""
        manager = StreamManager(buffer_size=10000)

        # Monitor memory usage
        process = psutil.Process()
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB

        # Generate and buffer large amounts of data
        for i in range(100):
            large_data = np.random.randn(1000, 64)  # 64-channel data
            # Simulate buffering
            time.sleep(0.01)

        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory

        # Memory increase should be reasonable (<100MB)
        assert memory_increase < 100

    def test_concurrent_connections(self):
        """Test handling multiple concurrent stream connections."""
        manager = StreamManager()

        # Mock multiple streams
        mock_streams = []
        for i in range(5):
            mock_stream = Mock()
            mock_stream.name.return_value = f'Stream_{i}'
            mock_stream.type.return_value = 'EEG'
            mock_stream.nominal_srate.return_value = 500.0
            mock_streams.append(mock_stream)

        with patch('pylsl.resolve_streams', return_value=mock_streams):
            streams = manager.discover_streams()
            assert len(streams) == 5

            # Test connection to all streams
            result = manager.connect_to_streams(streams)
            assert result is True

            # Verify all streams connected
            assert len(manager.streams) == 5
```

## ⚡ Performance Optimization

### Memory Management

#### Buffer Size Optimization
```python
# Optimize buffer sizes based on sampling rates
def calculate_optimal_buffer_size(sampling_rate: float, duration: float = 10.0) -> int:
    """Calculate optimal buffer size for given sampling rate."""
    samples_needed = int(sampling_rate * duration)
    # Round to nearest 1000 for efficient memory allocation
    return round(samples_needed / 1000) * 1000

# Usage
eeg_buffer = calculate_optimal_buffer_size(500.0)  # 5000 samples
ecg_buffer = calculate_optimal_buffer_size(250.0)  # 2500 samples

manager = StreamManager(
    buffer_size=min(eeg_buffer, ecg_buffer)  # Use smaller buffer
)
```

#### Memory-Efficient Data Structures
```python
import numpy as np
from typing import Dict, Any

class MemoryEfficientBuffer:
    """Memory-efficient circular buffer for stream data."""

    def __init__(self, max_size: int, dtype: np.dtype = np.float64):
        self.max_size = max_size
        self.dtype = dtype
        self.buffer = np.empty((max_size, 0), dtype=dtype)  # Empty initially
        self.current_size = 0

    def append(self, data: np.ndarray) -> None:
        """Append new data to buffer."""
        if data.shape[1] != self.buffer.shape[1]:
            # Resize buffer if channel count changed
            self._resize_channels(data.shape[1])

        # Circular buffer logic
        new_size = self.current_size + data.shape[0]
        if new_size > self.max_size:
            # Remove old data
            excess = new_size - self.max_size
            self.buffer = self.buffer[excess:]
            self.current_size = self.max_size

        # Add new data
        self.buffer = np.vstack([self.buffer, data]) if self.current_size > 0 else data
        self.current_size = min(self.current_size + data.shape[0], self.max_size)

    def _resize_channels(self, new_channels: int) -> None:
        """Resize buffer for different channel count."""
        if self.current_size == 0:
            self.buffer = np.empty((self.max_size, new_channels), dtype=self.dtype)
        else:
            new_buffer = np.empty((self.max_size, new_channels), dtype=self.dtype)
            old_channels = self.buffer.shape[1]
            copy_channels = min(old_channels, new_channels)
            new_buffer[:self.current_size, :copy_channels] = self.buffer[:self.current_size, :copy_channels]
            self.buffer = new_buffer
```

### CPU Optimization

#### Parallel Processing
```python
from concurrent.futures import ThreadPoolExecutor
from typing import List, Callable
import numpy as np

class ParallelProcessor:
    """Parallel processing for multiple streams."""

    def __init__(self, n_workers: int = 4):
        self.executor = ThreadPoolExecutor(max_workers=n_workers)
        self.futures = []

    def process_streams_parallel(
        self,
        stream_data: Dict[str, np.ndarray],
        processors: Dict[str, Callable]
    ) -> Dict[str, np.ndarray]:
        """Process multiple streams in parallel."""
        results = {}

        # Submit processing tasks
        for stream_name, data in stream_data.items():
            if stream_name in processors:
                future = self.executor.submit(processors[stream_name], data)
                self.futures.append((stream_name, future))

        # Collect results
        for stream_name, future in self.futures:
            try:
                results[stream_name] = future.result(timeout=1.0)
            except Exception as e:
                print(f"Error processing {stream_name}: {e}")

        # Clean up completed futures
        self.futures.clear()

        return results
```

#### Efficient Data Transfer
```python
class OptimizedDataTransfer:
    """Optimized data transfer between components."""

    def __init__(self, shared_memory_size: int = 1024 * 1024):  # 1MB
        self.shared_memory = np.empty(shared_memory_size, dtype=np.float64)
        self.memory_offset = 0

    def transfer_data(self, data: np.ndarray) -> memoryview:
        """Transfer data using shared memory."""
        data_size = data.nbytes

        if self.memory_offset + data_size > len(self.shared_memory):
            self.memory_offset = 0  # Reset if overflow

        # Copy to shared memory
        end_offset = self.memory_offset + data_size
        self.shared_memory[self.memory_offset:end_offset] = data.flatten()

        # Return memory view for zero-copy access
        memory_view = self.shared_memory[self.memory_offset:end_offset]
        self.memory_offset = end_offset

        return memory_view
```

### Network Optimization

#### Connection Pooling
```python
from typing import Dict, Any
import time

class ConnectionPool:
    """Connection pool for efficient stream management."""

    def __init__(self, max_connections: int = 10, timeout: float = 5.0):
        self.max_connections = max_connections
        self.timeout = timeout
        self.active_connections = {}
        self.connection_pool = []

    def get_connection(self, stream_name: str) -> Any:
        """Get or create connection for stream."""
        if stream_name in self.active_connections:
            return self.active_connections[stream_name]

        # Reuse from pool if available
        if self.connection_pool:
            connection = self.connection_pool.pop()
            self.active_connections[stream_name] = connection
            return connection

        # Create new connection
        connection = self._create_connection(stream_name)
        self.active_connections[stream_name] = connection
        return connection

    def release_connection(self, stream_name: str) -> None:
        """Release connection back to pool."""
        if stream_name in self.active_connections:
            connection = self.active_connections.pop(stream_name)
            self.connection_pool.append(connection)
```

#### Bandwidth Optimization
```python
class BandwidthOptimizer:
    """Optimize bandwidth usage for network streams."""

    def __init__(self, target_bandwidth: float = 100e6):  # 100 Mbps
        self.target_bandwidth = target_bandwidth
        self.compression_enabled = True
        self.data_compression = 'lz4'

    def compress_data(self, data: np.ndarray) -> bytes:
        """Compress data for efficient transmission."""
        if not self.compression_enabled:
            return data.tobytes()

        # Apply compression
        compressed_data = lz4.frame.compress(
            data.tobytes(),
            compression_level=lz4.frame.COMPRESSIONLEVEL_MINHC
        )
        return compressed_data

    def optimize_sampling_rate(self, current_rate: float) -> float:
        """Optimize sampling rate based on available bandwidth."""
        estimated_bandwidth = current_rate * 8 * 64  # 64-bit samples

        if estimated_bandwidth > self.target_bandwidth:
            # Reduce sampling rate
            optimized_rate = self.target_bandwidth / (8 * 64)
            return max(optimized_rate, 1.0)  # Minimum 1 Hz

        return current_rate
```

## 🐛 Debugging and Profiling

### Logging Configuration

```python
import logging
from lsl_receiver import StreamManager

# Configure detailed logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('stream_receiver.log'),
        logging.StreamHandler()
    ]
)

# Create logger for debugging
logger = logging.getLogger('LSLReceiver')

# Enable debug logging
manager = StreamManager(debug=True)
```

### Performance Profiling

```python
import cProfile
import pstats
from lsl_receiver import StreamManager

def profile_stream_reception():
    """Profile stream reception performance."""
    manager = StreamManager()

    # Profile stream discovery
    profiler = cProfile.Profile()
    profiler.enable()

    streams = manager.discover_streams()
    manager.connect_to_streams(streams)
    manager.start_receiving()

    # Simulate data reception
    for i in range(100):
        data = manager.get_latest_data()
        time.sleep(0.01)

    manager.stop_receiving()
    profiler.disable()

    # Analyze results
    stats = pstats.Stats(profiler)
    stats.sort_stats('cumulative')
    stats.print_stats(20)  # Top 20 functions

# Run profiler
profile_stream_reception()
```

### Memory Profiling

```python
import tracemalloc
from lsl_receiver import StreamManager

def profile_memory_usage():
    """Profile memory usage during stream reception."""
    tracemalloc.start()

    manager = StreamManager(buffer_size=5000)

    # Take initial memory snapshot
    snapshot1 = tracemalloc.take_snapshot()

    # Simulate data reception
    manager.start_receiving()

    for i in range(1000):
        data = manager.get_latest_data(n_samples=100)
        time.sleep(0.001)

    # Take final memory snapshot
    snapshot2 = tracemalloc.take_snapshot()

    # Analyze memory usage
    stats = snapshot2.compare_to(snapshot1, 'lineno')
    for stat in stats[:10]:  # Top 10 memory differences
        print(stat)

    tracemalloc.stop()

# Run memory profiler
profile_memory_usage()
```

### Debug Utilities

```python
class StreamDebugUtils:
    """Utilities for debugging stream issues."""

    @staticmethod
    def print_stream_info(stream_info):
        """Print detailed stream information."""
        print(f"Stream Name: {stream_info.name()}")
        print(f"Stream Type: {stream_info.type()}")
        print(f"Channel Count: {stream_info.channel_count()}")
        print(f"Sampling Rate: {stream_info.nominal_srate()} Hz")
        print(f"Data Type: {stream_info.channel_format()}")
        print(f"Source ID: {stream_info.source_id()}")
        print(f"Created At: {stream_info.created_at()}")

    @staticmethod
    def validate_stream_connection(stream_inlet):
        """Validate stream connection."""
        try:
            # Test data retrieval
            samples, timestamps = stream_inlet.pull_sample(timeout=1.0)

            if samples is None:
                print("❌ No samples received")
                return False

            print(f"✅ Connection valid - {len(samples)} channels")
            print(f"Sample: {samples[:5]}...")  # First 5 channels
            return True

        except Exception as e:
            print(f"❌ Connection error: {e}")
            return False

    @staticmethod
    def monitor_data_rate(stream_inlet, duration=10):
        """Monitor data rate for a stream."""
        import time

        start_time = time.time()
        sample_count = 0

        print("Monitoring data rate...")

        while time.time() - start_time < duration:
            samples, timestamps = stream_inlet.pull_sample(timeout=0.1)

            if samples is not None:
                sample_count += 1

            time.sleep(0.01)

        elapsed = time.time() - start_time
        rate = sample_count / elapsed

        print(f"Data rate: {rate".1f"} samples/sec")
        print(f"Total samples: {sample_count}")
        print(f"Duration: {elapsed".2f"} seconds")

        return rate
```

---

*This development guide is maintained by the lab's technical team. For updates or corrections, please create an issue or submit a pull request.*
