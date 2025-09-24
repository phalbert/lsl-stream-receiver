"""
Quality Assessment for LSL Streams
=================================

Assesses and monitors the quality of LSL stream data.
"""

import time
import numpy as np
from typing import Dict, List, Any, Optional
from collections import defaultdict
from loguru import logger


class QualityAssessor:
    """Assesses quality of LSL stream data."""

    def __init__(self,
                 check_interval: float = 30.0,
                 required_sampling_rate_tolerance: float = 0.1,
                 max_missing_data_ratio: float = 0.1):
        """
        Initialize quality assessor.

        Args:
            check_interval: Seconds between quality checks
            required_sampling_rate_tolerance: Tolerance for sampling rate deviation (fraction)
            max_missing_data_ratio: Maximum acceptable ratio of missing data
        """
        self.check_interval = check_interval
        self.sampling_rate_tolerance = required_sampling_rate_tolerance
        self.max_missing_data_ratio = max_missing_data_ratio

        self.last_check_time = 0
        self.stream_history: Dict[str, List] = defaultdict(list)
        self.quality_history: Dict[str, List] = defaultdict(list)

    def assess_quality(self, stream_infos: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """
        Assess quality of all streams.

        Args:
            stream_infos: Dictionary of stream information

        Returns:
            Quality assessment report
        """
        current_time = time.time()
        report = {
            'timestamp': current_time,
            'streams': {},
            'overall_quality': 'good',
            'issues': []
        }

        overall_score = 0
        stream_count = 0

        for stream_name, info in stream_infos.items():
            stream_quality = self._assess_single_stream(stream_name, info, current_time)
            report['streams'][stream_name] = stream_quality

            if stream_quality['status'] == 'critical':
                report['overall_quality'] = 'critical'
                report['issues'].append(f"Critical issue with {stream_name}: {stream_quality['issues']}")
            elif stream_quality['status'] == 'warning':
                if report['overall_quality'] != 'critical':
                    report['overall_quality'] = 'warning'
                report['issues'].append(f"Warning for {stream_name}: {stream_quality['issues']}")

            overall_score += stream_quality['score']
            stream_count += 1

        if stream_count > 0:
            report['overall_score'] = overall_score / stream_count

        self.last_check_time = current_time
        logger.info(f"Quality assessment completed: {report['overall_quality']} (score: {report.get('overall_score', 0):.2f})")

        return report

    def _assess_single_stream(self, stream_name: str, info: Dict[str, Any], current_time: float) -> Dict[str, Any]:
        """Assess quality of a single stream."""
        assessment = {
            'status': 'good',
            'score': 1.0,
            'issues': [],
            'metrics': {}
        }

        # Check connection status
        if not info.get('connected', False):
            assessment['status'] = 'critical'
            assessment['score'] = 0.0
            assessment['issues'].append('Stream not connected')
            return assessment

        # Check sampling rate
        nominal_rate = info.get('sampling_rate', 0)
        if nominal_rate > 0:
            expected_samples = nominal_rate * self.check_interval
            actual_samples = info.get('samples_received', 0)

            # This is a simplified check - in practice you'd track actual sampling
            rate_deviation = abs(nominal_rate - actual_samples / self.check_interval) / nominal_rate

            if rate_deviation > self.sampling_rate_tolerance:
                assessment['status'] = 'warning' if rate_deviation < 0.5 else 'critical'
                assessment['issues'].append(f'Sampling rate deviation: {rate_deviation:.2f}')
                assessment['score'] *= (1 - rate_deviation)

            assessment['metrics']['sampling_rate_deviation'] = rate_deviation
            assessment['metrics']['expected_samples'] = expected_samples
            assessment['metrics']['actual_samples'] = actual_samples

        # Check for connection errors
        connection_errors = info.get('connection_errors', 0)
        if connection_errors > 0:
            assessment['issues'].append(f'Connection errors: {connection_errors}')
            assessment['score'] *= max(0.5, 1 - connection_errors * 0.2)

        # Check data staleness
        last_sample_time = info.get('last_sample_time', 0)
        time_since_last_sample = current_time - last_sample_time if last_sample_time > 0 else float('inf')

        if time_since_last_sample > self.check_interval * 2:
            assessment['status'] = 'critical'
            assessment['issues'].append(f'No recent samples (last: {time_since_last_sample:.1f}s ago)')
            assessment['score'] *= 0.1
        elif time_since_last_sample > self.check_interval:
            assessment['status'] = 'warning'
            assessment['issues'].append(f'Stale data (last: {time_since_last_sample:.1f}s ago)')
            assessment['score'] *= 0.7

        assessment['metrics']['time_since_last_sample'] = time_since_last_sample
        assessment['metrics']['connection_errors'] = connection_errors

        # Ensure score is between 0 and 1
        assessment['score'] = max(0.0, min(1.0, assessment['score']))

        return assessment

    def get_quality_history(self, stream_name: Optional[str] = None) -> Dict[str, List]:
        """Get quality history for streams."""
        if stream_name:
            return {stream_name: self.quality_history[stream_name]}
        return dict(self.quality_history)

    def get_stream_statistics(self, stream_name: str) -> Dict[str, Any]:
        """Get comprehensive statistics for a stream."""
        if stream_name not in self.quality_history:
            return {}

        history = self.quality_history[stream_name]
        if not history:
            return {}

        scores = [h.get('score', 0) for h in history]
        statuses = [h.get('status', 'unknown') for h in history]

        return {
            'current_score': scores[-1] if scores else 0,
            'average_score': np.mean(scores),
            'min_score': np.min(scores),
            'max_score': np.max(scores),
            'good_count': statuses.count('good'),
            'warning_count': statuses.count('warning'),
            'critical_count': statuses.count('critical'),
            'total_checks': len(scores)
        }

    def reset_history(self, stream_name: Optional[str] = None):
        """Reset quality history."""
        if stream_name:
            self.quality_history[stream_name] = []
            logger.info(f"Reset quality history for: {stream_name}")
        else:
            self.quality_history.clear()
            logger.info("Reset quality history for all streams")


class SignalQualityAnalyzer:
    """Analyzes signal quality from raw data."""

    @staticmethod
    def analyze_signal_quality(samples: List[Dict[str, Any]],
                             window_size: int = 100) -> Dict[str, Any]:
        """
        Analyze signal quality metrics from a list of samples.

        Args:
            samples: List of sample dictionaries
            window_size: Size of analysis window

        Returns:
            Dictionary with quality metrics
        """
        if not samples:
            return {'error': 'No samples provided'}

        try:
            # Extract values for each channel
            channel_data = defaultdict(list)
            timestamps = []

            for sample in samples:
                timestamps.append(sample.get('timestamp', 0))
                values = sample.get('values', [])
                for i, value in enumerate(values):
                    channel_data[f'ch_{i}'].append(value)

            analysis = {
                'total_samples': len(samples),
                'channels': len(channel_data),
                'duration': max(timestamps) - min(timestamps) if timestamps else 0,
                'channels_analysis': {}
            }

            # Analyze each channel
            for channel_name, values in channel_data.items():
                if len(values) < 2:
                    continue

                values_array = np.array(values)

                # Basic statistics
                stats = {
                    'mean': float(np.mean(values_array)),
                    'std': float(np.std(values_array)),
                    'min': float(np.min(values_array)),
                    'max': float(np.max(values_array)),
                    'range': float(np.max(values_array) - np.min(values_array))
                }

                # Signal quality metrics
                # SNR approximation (signal power / noise power)
                # Using median absolute deviation as noise estimate
                mad = np.median(np.abs(values_array - np.median(values_array)))
                signal_power = np.mean(values_array ** 2)
                noise_power = mad ** 2
                snr = signal_power / noise_power if noise_power > 0 else float('inf')

                # Flat segments detection (potential signal loss)
                flat_ratio = SignalQualityAnalyzer._detect_flat_segments(values_array)

                # Missing data detection
                missing_ratio = SignalQualityAnalyzer._detect_missing_data(values_array)

                channel_analysis = {
                    **stats,
                    'snr_db': float(10 * np.log10(snr)) if snr < float('inf') else float('inf'),
                    'flat_ratio': float(flat_ratio),
                    'missing_ratio': float(missing_ratio),
                    'quality_score': SignalQualityAnalyzer._compute_quality_score(
                        snr, flat_ratio, missing_ratio
                    )
                }

                analysis['channels_analysis'][channel_name] = channel_analysis

            return analysis

        except Exception as e:
            logger.error(f"Error analyzing signal quality: {e}")
            return {'error': str(e)}

    @staticmethod
    def _detect_flat_segments(values: np.ndarray, threshold: float = 1e-6) -> float:
        """Detect ratio of flat (unchanging) segments in signal."""
        if len(values) < 2:
            return 0.0

        differences = np.abs(np.diff(values))
        flat_samples = np.sum(differences < threshold)
        return flat_samples / len(values)

    @staticmethod
    def _detect_missing_data(values: np.ndarray, nan_threshold: float = 1e-10) -> float:
        """Detect ratio of missing/invalid data points."""
        if len(values) == 0:
            return 1.0

        nan_count = np.sum(np.isnan(values)) + np.sum(np.abs(values) < nan_threshold)
        return nan_count / len(values)

    @staticmethod
    def _compute_quality_score(snr: float, flat_ratio: float, missing_ratio: float) -> float:
        """Compute overall quality score from individual metrics."""
        # Weights for different quality aspects
        weights = {
            'snr': 0.5,      # Signal-to-noise ratio
            'flatness': 0.3, # Penalty for flat segments
            'completeness': 0.2  # Penalty for missing data
        }

        # Normalize metrics to [0,1] range
        snr_score = min(1.0, snr / 20.0)  # Assume 20dB is good quality

        flatness_penalty = 1.0 - min(1.0, flat_ratio * 10)  # Penalize high flatness
        completeness_score = 1.0 - missing_ratio  # Higher is better

        quality_score = (
            weights['snr'] * snr_score +
            weights['flatness'] * flatness_penalty +
            weights['completeness'] * completeness_score
        )

        return max(0.0, min(1.0, quality_score))


def assess_stream_quality(stream_name: str,
                         samples: List[Dict[str, Any]],
                         quality_assessor: QualityAssessor) -> Dict[str, Any]:
    """
    Convenience function to assess quality of a specific stream.

    Args:
        stream_name: Name of the stream
        samples: List of recent samples
        quality_assessor: QualityAssessor instance

    Returns:
        Quality assessment results
    """
    stream_info = {'connected': True, 'samples_received': len(samples)}
    quality_report = quality_assessor.assess_quality({stream_name: stream_info})

    # Add signal quality analysis if samples are provided
    if samples:
        signal_quality = SignalQualityAnalyzer.analyze_signal_quality(samples)
        quality_report['streams'][stream_name]['signal_quality'] = signal_quality

    return quality_report
