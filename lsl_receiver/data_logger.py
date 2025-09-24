"""
Data Logger for LSL Streams
==========================

Handles logging of LSL stream data to various formats with comprehensive metadata.
"""

import os
import json
import csv
import time
from datetime import datetime
from typing import Dict, List, Optional, Any, Union
import pandas as pd
from pathlib import Path
from loguru import logger


class DataLogger:
    """Configurable data logger for LSL streams."""

    def __init__(self,
                 output_dir: str = "lsl_data",
                 formats: List[str] = None,
                 include_metadata: bool = True,
                 quality_metrics: bool = True,
                 session_name: Optional[str] = None):
        """
        Initialize data logger.

        Args:
            output_dir: Directory for output files
            formats: List of output formats ['csv', 'json', 'parquet']
            include_metadata: Whether to include comprehensive metadata
            quality_metrics: Whether to compute and log quality metrics
            session_name: Optional session name for file organization
        """
        self.output_dir = Path(output_dir)
        self.formats = formats or ['csv', 'json']
        self.include_metadata = include_metadata
        self.quality_metrics = quality_metrics
        self.session_name = session_name or f"session_{int(time.time())}"

        # Create output structure
        self.session_dir = self.output_dir / self.session_name
        self.session_dir.mkdir(parents=True, exist_ok=True)

        # File handles
        self.csv_file = None
        self.csv_writer = None
        self.json_file = None
        self.metadata = {}

        # Data buffers
        self.data_buffer = []
        self.buffer_size = 1000  # Save every 1000 samples
        self.last_save_time = time.time()

        self._initialize_metadata()
        self._setup_files()

        logger.info(f"DataLogger initialized for session: {self.session_name}")

    def _initialize_metadata(self):
        """Initialize metadata dictionary."""
        self.metadata = {
            'session_name': self.session_name,
            'start_time': datetime.now().isoformat(),
            'system_info': {
                'python_version': f"{os.sys.version_info.major}.{os.sys.version_info.minor}",
                'platform': os.sys.platform
            },
            'streams': {},
            'data_quality': {
                'samples_logged': 0,
                'last_quality_check': None
            }
        }

    def _setup_files(self):
        """Setup output files and writers."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # CSV file for main data
        csv_path = self.session_dir / f"lsl_data_{timestamp}.csv"
        self.csv_file = open(csv_path, 'w', newline='', encoding='utf-8')
        self._setup_csv_writer()

        # JSON file for structured data
        json_path = self.session_dir / f"lsl_data_{timestamp}.json"
        self.json_file = open(json_path, 'w', encoding='utf-8')

        # Metadata file
        metadata_path = self.session_dir / f"session_metadata_{timestamp}.json"
        self.metadata_file = metadata_path

        logger.info(f"Output files initialized in: {self.session_dir}")

    def _setup_csv_writer(self):
        """Setup CSV writer with appropriate fieldnames."""
        fieldnames = [
            'timestamp',
            'lsl_timestamp',
            'stream_name',
            'stream_type',
            'sampling_rate',
            'sample_index'
        ]

        # Add channel value columns (dynamically based on max channels seen)
        self.csv_writer = csv.DictWriter(self.csv_file, fieldnames=fieldnames)
        self.csv_writer.writeheader()

    def _update_metadata(self, stream_name: str, sample_data: Dict[str, Any]):
        """Update metadata with stream information."""
        if stream_name not in self.metadata['streams']:
            self.metadata['streams'][stream_name] = {
                'stream_type': sample_data.get('stream_type'),
                'sampling_rate': sample_data.get('sampling_rate'),
                'first_sample_time': sample_data.get('timestamp'),
                'samples_count': 0,
                'channels': len(sample_data.get('values', []))
            }

        self.metadata['streams'][stream_name]['samples_count'] += 1
        self.metadata['streams'][stream_name]['last_sample_time'] = sample_data.get('timestamp')

    def log_samples(self, samples: List[Dict[str, Any]]):
        """
        Log a batch of samples.

        Args:
            samples: List of sample dictionaries
        """
        if not samples:
            return

        # Add samples to buffer
        self.data_buffer.extend(samples)
        self.metadata['data_quality']['samples_logged'] += len(samples)

        # Update metadata for each stream
        for sample in samples:
            stream_name = sample.get('stream_name')
            if stream_name:
                self._update_metadata(stream_name, sample)

        # Write to files if buffer is full or enough time has passed
        current_time = time.time()
        if (len(self.data_buffer) >= self.buffer_size or
            current_time - self.last_save_time > 30):  # Save every 30 seconds minimum
            self._save_buffer()
            self.last_save_time = current_time

    def _save_buffer(self):
        """Save buffered data to files."""
        if not self.data_buffer:
            return

        try:
            # Save to CSV
            if 'csv' in self.formats and self.csv_writer:
                self._write_csv_data(self.data_buffer)

            # Save to JSON
            if 'json' in self.formats and self.json_file:
                self._write_json_data(self.data_buffer)

            # Clear buffer
            self.data_buffer = []

            logger.debug(f"Saved {len(self.data_buffer)} samples to files")

        except Exception as e:
            logger.error(f"Error saving data buffer: {e}")

    def _write_csv_data(self, samples: List[Dict[str, Any]]):
        """Write samples to CSV file."""
        for sample in samples:
            csv_row = {
                'timestamp': sample.get('timestamp'),
                'lsl_timestamp': sample.get('lsl_timestamp'),
                'stream_name': sample.get('stream_name'),
                'stream_type': sample.get('stream_type'),
                'sampling_rate': sample.get('sampling_rate'),
                'sample_index': sample.get('sample_index')
            }

            # Add channel values (assuming max 16 channels for now)
            values = sample.get('values', [])
            for i, value in enumerate(values[:16]):  # Limit to 16 channels
                csv_row[f'ch_{i}'] = value

            self.csv_writer.writerow(csv_row)

        self.csv_file.flush()

    def _write_json_data(self, samples: List[Dict[str, Any]]):
        """Write samples to JSON file."""
        # Convert to JSON-serializable format
        json_data = []
        for sample in samples:
            json_sample = {
                'timestamp': sample.get('timestamp'),
                'lsl_timestamp': sample.get('lsl_timestamp'),
                'stream_name': sample.get('stream_name'),
                'stream_type': sample.get('stream_type'),
                'sampling_rate': sample.get('sampling_rate'),
                'sample_index': sample.get('sample_index'),
                'values': sample.get('values', [])
            }
            json_data.append(json_sample)

        # Write as JSON lines (append mode)
        for item in json_data:
            self.json_file.write(json.dumps(item) + '\n')

        self.json_file.flush()

    def save_session_summary(self):
        """Save comprehensive session summary."""
        try:
            self.metadata['end_time'] = datetime.now().isoformat()
            self.metadata['total_samples'] = sum(
                stream_info['samples_count']
                for stream_info in self.metadata['streams'].values()
            )

            # Save metadata
            with open(self.metadata_file, 'w', encoding='utf-8') as f:
                json.dump(self.metadata, f, indent=2, default=str)

            # Create summary report
            summary = self._generate_summary()
            summary_file = self.session_dir / f"session_summary_{int(time.time())}.json"

            with open(summary_file, 'w', encoding='utf-8') as f:
                json.dump(summary, f, indent=2, default=str)

            logger.success(f"Session summary saved to: {summary_file}")

        except Exception as e:
            logger.error(f"Error saving session summary: {e}")

    def _generate_summary(self) -> Dict[str, Any]:
        """Generate comprehensive session summary."""
        total_duration = time.time() - time.mktime(
            time.strptime(self.metadata['start_time'].split('T')[0], '%Y-%m-%d')
        )

        summary = {
            'session_info': {
                'name': self.session_name,
                'duration_seconds': total_duration,
                'total_samples': self.metadata.get('total_samples', 0),
                'streams_count': len(self.metadata.get('streams', {}))
            },
            'streams_summary': {},
            'data_quality': self.metadata.get('data_quality', {}),
            'output_files': {
                'directory': str(self.session_dir),
                'files': list(self.session_dir.glob('*'))
            }
        }

        # Stream-specific summaries
        for stream_name, stream_info in self.metadata.get('streams', {}).items():
            summary['streams_summary'][stream_name] = {
                'type': stream_info.get('stream_type'),
                'sampling_rate': stream_info.get('sampling_rate'),
                'samples_count': stream_info.get('samples_count'),
                'channels': stream_info.get('channels'),
                'duration_seconds': (
                    stream_info.get('last_sample_time', 0) -
                    stream_info.get('first_sample_time', 0)
                )
            }

        return summary

    def log_event(self, event_type: str, event_data: Dict[str, Any]):
        """Log a custom event."""
        event = {
            'timestamp': time.time(),
            'event_type': event_type,
            'event_data': event_data
        }

        # Save to separate events file
        events_file = self.session_dir / "events.jsonl"
        with open(events_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(event) + '\n')

        logger.info(f"Event logged: {event_type}")

    def close(self):
        """Close all file handles and save final data."""
        try:
            # Save any remaining buffered data
            self._save_buffer()

            # Close files
            if self.csv_file:
                self.csv_file.close()

            if self.json_file:
                self.json_file.close()

            # Save session summary
            self.save_session_summary()

            logger.success(f"DataLogger closed for session: {self.session_name}")

        except Exception as e:
            logger.error(f"Error closing DataLogger: {e}")


# Convenience functions
def create_csv_logger(output_dir: str = "lsl_data",
                     session_name: Optional[str] = None) -> DataLogger:
    """Create a CSV-only data logger."""
    return DataLogger(
        output_dir=output_dir,
        formats=['csv'],
        session_name=session_name
    )

def create_json_logger(output_dir: str = "lsl_data",
                      session_name: Optional[str] = None) -> DataLogger:
    """Create a JSON-only data logger."""
    return DataLogger(
        output_dir=output_dir,
        formats=['json'],
        session_name=session_name
    )

def create_multi_format_logger(output_dir: str = "lsl_data",
                              session_name: Optional[str] = None) -> DataLogger:
    """Create a multi-format data logger (CSV + JSON)."""
    return DataLogger(
        output_dir=output_dir,
        formats=['csv', 'json'],
        include_metadata=True,
        quality_metrics=True,
        session_name=session_name
    )
