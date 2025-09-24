"""
LSL Stream Receiver Library
==========================

A comprehensive library for receiving and managing data from multiple LSL (Lab Streaming Layer) streams.

Main components:
- StreamManager: Core class for managing multiple LSL streams
- DataLogger: Configurable data logging with quality metrics
- QualityAssessor: Signal quality assessment and validation

Example:
    from lsl_receiver import StreamManager

    manager = StreamManager()
    manager.start_receiving()
    data = manager.get_latest_data()
    manager.stop_receiving()
"""

from .core import StreamManager
from .data_logger import DataLogger
from .quality_assessor import QualityAssessor

__version__ = "1.0.0"
__all__ = ["StreamManager", "DataLogger", "QualityAssessor"]
