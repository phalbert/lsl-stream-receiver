"""
Core LSL Stream Receiver
=======================

Main classes for receiving and managing LSL streams.
"""

import time
import threading
from typing import Dict, List, Optional, Any, Callable
from collections import defaultdict
import numpy as np
from pylsl import StreamInlet, resolve_streams, StreamInfo
from loguru import logger

from .data_logger import DataLogger
from .quality_assessor import QualityAssessor


class StreamReceiver:
    """Handles receiving data from a single LSL stream."""

    def __init__(self, stream_info: StreamInfo, auto_reconnect: bool = True):
        """
        Initialize stream receiver.

        Args:
            stream_info: LSL StreamInfo object
            auto_reconnect: Whether to automatically reconnect on disconnection
        """
        self.stream_info = stream_info
        self.stream_name = stream_info.name()
        self.stream_type = stream_info.type()
        self.sampling_rate = stream_info.nominal_srate()
        self.channel_count = stream_info.channel_count()

        self.inlet: Optional[StreamInlet] = None
        self.connected = False
        self.auto_reconnect = auto_reconnect
        self.last_sample_time = 0
        self.samples_received = 0
        self.connection_errors = 0

        self._data_buffer = []
        self._max_buffer_size = 1000  # Keep last 1000 samples per stream
        self._lock = threading.Lock()

        self.connect()

    def connect(self) -> bool:
        """Connect to the LSL stream."""
        try:
            logger.info(f"Connecting to stream: {self.stream_name}")
            self.inlet = StreamInlet(self.stream_info)
            self.connected = True
            self.connection_errors = 0
            logger.success(f"Successfully connected to: {self.stream_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to {self.stream_name}: {e}")
            self.connected = False
            self.connection_errors += 1
            return False

    def disconnect(self):
        """Disconnect from the stream."""
        if self.inlet:
            try:
                self.inlet.close_stream()
            except Exception as e:
                logger.warning(f"Error closing stream {self.stream_name}: {e}")
        self.connected = False
        logger.info(f"Disconnected from: {self.stream_name}")

    def pull_samples(self, timeout: float = 1.0, max_samples: int = 100) -> List[Dict[str, Any]]:
        """
        Pull samples from the stream.

        Args:
            timeout: Timeout for pulling samples
            max_samples: Maximum number of samples to pull

        Returns:
            List of sample dictionaries with metadata
        """
        if not self.connected or not self.inlet:
            if self.auto_reconnect and self.connection_errors < 5:
                self.connect()
            return []

        try:
            samples, timestamps = self.inlet.pull_chunk(timeout=timeout, max_samples=max_samples)

            if not samples:
                return []

            current_time = time.time()
            sample_data = []

            for sample, timestamp in zip(samples, timestamps):
                self.samples_received += 1
                self.last_sample_time = current_time

                sample_dict = {
                    'timestamp': current_time,
                    'lsl_timestamp': timestamp,
                    'stream_name': self.stream_name,
                    'stream_type': self.stream_type,
                    'sampling_rate': self.sampling_rate,
                    'values': sample,
                    'sample_index': self.samples_received
                }

                sample_data.append(sample_dict)

            # Add to buffer (thread-safe)
            with self._lock:
                self._data_buffer.extend(sample_data)
                if len(self._data_buffer) > self._max_buffer_size:
                    self._data_buffer = self._data_buffer[-self._max_buffer_size:]

            return sample_data

        except Exception as e:
            logger.error(f"Error pulling samples from {self.stream_name}: {e}")
            self.connected = False
            self.connection_errors += 1
            return []

    def get_latest_data(self, n_samples: int = 10) -> List[Dict[str, Any]]:
        """Get the latest n samples from buffer."""
        with self._lock:
            return self._data_buffer[-n_samples:] if self._data_buffer else []

    def get_stream_info(self) -> Dict[str, Any]:
        """Get comprehensive stream information."""
        return {
            'name': self.stream_name,
            'type': self.stream_type,
            'sampling_rate': self.sampling_rate,
            'channels': self.channel_count,
            'connected': self.connected,
            'samples_received': self.samples_received,
            'last_sample_time': self.last_sample_time,
            'connection_errors': self.connection_errors,
            'auto_reconnect': self.auto_reconnect
        }


class StreamManager:
    """
    Main class for managing multiple LSL streams.

    Provides high-level interface for:
    - Stream discovery and connection
    - Multi-stream data collection
    - Quality monitoring
    - Data logging
    """

    def __init__(self,
                 target_streams: Optional[List[str]] = None,
                 auto_discovery: bool = True,
                 reconnect_attempts: int = 3,
                 quality_check_interval: float = 30.0):
        """
        Initialize StreamManager.

        Args:
            target_streams: List of specific stream names to connect to (None for all)
            auto_discovery: Whether to automatically discover available streams
            reconnect_attempts: Number of reconnection attempts per stream
            quality_check_interval: Seconds between quality assessments
        """
        self.target_streams = target_streams
        self.auto_discovery = auto_discovery
        self.reconnect_attempts = reconnect_attempts
        self.quality_check_interval = quality_check_interval

        self.streams: Dict[str, StreamReceiver] = {}
        self.data_logger: Optional[DataLogger] = None
        self.quality_assessor: Optional[QualityAssessor] = None

        self.running = False
        self.receiver_thread: Optional[threading.Thread] = None
        self.last_quality_check = 0

        # Data storage
        self.latest_data: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        self._data_lock = threading.Lock()

        logger.info("StreamManager initialized")

    def discover_streams(self) -> Dict[str, StreamInfo]:
        """Discover available LSL streams."""
        logger.info("Discovering LSL streams...")
        available_streams = {}

        try:
            streams = resolve_streams()
            for stream in streams:
                stream_name = stream.name()
                if self.target_streams is None or stream_name in self.target_streams:
                    available_streams[stream_name] = stream
                    logger.info(f"Found stream: {stream_name} ({stream.type()}, {stream.nominal_srate()} Hz)")
                else:
                    logger.debug(f"Skipping stream: {stream_name}")

            logger.success(f"Discovered {len(available_streams)} target streams")
            return available_streams

        except Exception as e:
            logger.error(f"Error discovering streams: {e}")
            return {}

    def connect_to_streams(self, stream_infos: Dict[str, StreamInfo]) -> bool:
        """Connect to specified streams."""
        success_count = 0

        for stream_name, stream_info in stream_infos.items():
            try:
                receiver = StreamReceiver(stream_info)
                if receiver.connected:
                    self.streams[stream_name] = receiver
                    success_count += 1
                    logger.success(f"Connected to: {stream_name}")
                else:
                    logger.error(f"Failed to connect to: {stream_name}")

            except Exception as e:
                logger.error(f"Error creating receiver for {stream_name}: {e}")

        logger.info(f"Successfully connected to {success_count}/{len(stream_infos)} streams")
        return success_count > 0

    def start_receiving(self,
                       data_logger: Optional[DataLogger] = None,
                       quality_assessor: Optional[QualityAssessor] = None) -> bool:
        """
        Start receiving data from all connected streams.

        Args:
            data_logger: Optional data logger for saving data
            quality_assessor: Optional quality assessor for monitoring

        Returns:
            True if started successfully
        """
        if self.running:
            logger.warning("Already running")
            return True

        # Setup components
        self.data_logger = data_logger
        self.quality_assessor = quality_assessor

        if not self.streams:
            logger.info("No streams connected, attempting to discover and connect...")
            stream_infos = self.discover_streams()
            if not self.connect_to_streams(stream_infos):
                logger.error("No streams available to connect to")
                return False

        self.running = True
        self.receiver_thread = threading.Thread(target=self._receive_loop, daemon=True)
        self.receiver_thread.start()

        logger.success("Started receiving data from LSL streams")
        return True

    def stop_receiving(self):
        """Stop receiving data and clean up."""
        if not self.running:
            return

        logger.info("Stopping stream reception...")
        self.running = False

        if self.receiver_thread and self.receiver_thread.is_alive():
            self.receiver_thread.join(timeout=5.0)

        # Disconnect all streams
        for stream_name, receiver in self.streams.items():
            receiver.disconnect()

        logger.success("Stopped receiving data")

    def _receive_loop(self):
        """Main loop for receiving data from streams."""
        logger.info("Starting data reception loop")

        while self.running:
            try:
                # Pull data from all streams
                for stream_name, receiver in list(self.streams.items()):
                    samples = receiver.pull_samples(timeout=0.1, max_samples=50)

                    if samples:
                        # Update latest data (thread-safe)
                        with self._data_lock:
                            self.latest_data[stream_name].extend(samples)

                            # Keep only recent data to prevent memory issues
                            if len(self.latest_data[stream_name]) > 1000:
                                self.latest_data[stream_name] = self.latest_data[stream_name][-1000:]

                        # Log data if logger is configured
                        if self.data_logger:
                            self.data_logger.log_samples(samples)

                # Periodic quality assessment
                current_time = time.time()
                if (current_time - self.last_quality_check > self.quality_check_interval and
                    self.quality_assessor):
                    self._perform_quality_check()
                    self.last_quality_check = current_time

                # Small delay to prevent busy waiting
                time.sleep(0.01)

            except Exception as e:
                logger.error(f"Error in receive loop: {e}")
                time.sleep(1.0)  # Wait longer on errors

        logger.info("Data reception loop stopped")

    def _perform_quality_check(self):
        """Perform quality assessment on current streams."""
        try:
            stream_infos = {}
            for name, receiver in self.streams.items():
                stream_infos[name] = receiver.get_stream_info()

            if self.quality_assessor:
                quality_report = self.quality_assessor.assess_quality(stream_infos)
                logger.info(f"Quality check completed: {quality_report}")

        except Exception as e:
            logger.error(f"Error during quality check: {e}")

    def get_latest_data(self, stream_name: Optional[str] = None, n_samples: int = 10) -> Dict[str, Any]:
        """
        Get latest data from streams.

        Args:
            stream_name: If specified, get data from specific stream only
            n_samples: Number of recent samples to return per stream

        Returns:
            Dictionary with stream data
        """
        with self._data_lock:
            if stream_name:
                return {
                    stream_name: self.latest_data[stream_name][-n_samples:]
                    if stream_name in self.latest_data else []
                }
            else:
                return {
                    name: data[-n_samples:]
                    for name, data in self.latest_data.items()
                }

    def get_stream_info(self, stream_name: Optional[str] = None) -> Dict[str, Any]:
        """Get information about connected streams."""
        if stream_name:
            if stream_name in self.streams:
                return self.streams[stream_name].get_stream_info()
            else:
                return {}
        else:
            return {
                name: receiver.get_stream_info()
                for name, receiver in self.streams.items()
            }

    def get_status_summary(self) -> Dict[str, Any]:
        """Get comprehensive status summary."""
        return {
            'running': self.running,
            'connected_streams': len(self.streams),
            'total_samples_received': sum(r.samples_received for r in self.streams.values()),
            'stream_info': self.get_stream_info(),
            'latest_data_count': {
                name: len(data) for name, data in self.latest_data.items()
            }
        }

    def __del__(self):
        """Cleanup when object is destroyed."""
        self.stop_receiving()
