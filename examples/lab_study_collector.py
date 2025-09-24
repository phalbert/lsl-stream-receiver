#!/usr/bin/env python3
"""
Lab Study Data Collector
=======================

Complete example for collecting physiological data in a research study.
This demonstrates a typical lab workflow for multi-modal data collection.
"""

import time
import json
import argparse
from pathlib import Path
from datetime import datetime
from lsl_receiver import StreamManager, DataLogger, QualityAssessor
from lsl_receiver.data_logger import create_multi_format_logger


class LabStudyCollector:
    """Complete data collection system for lab studies."""

    def __init__(self, participant_id: str, study_name: str = "default_study"):
        self.participant_id = participant_id
        self.study_name = study_name

        # Setup session information
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.session_name = f"{participant_id}_{study_name}_{timestamp}"

        # Expected streams for a typical physiological study
        self.expected_streams = [
            'EEG', 'ECG', 'EDA', 'PPG', 'EyeTracking', 'Respiration'
        ]

        # Setup components
        self.manager = None
        self.logger = None
        self.assessor = None
        self.study_metadata = self._create_study_metadata()

    def _create_study_metadata(self) -> dict:
        """Create comprehensive study metadata."""
        return {
            'participant_id': self.participant_id,
            'study_name': self.study_name,
            'session_name': self.session_name,
            'start_time': datetime.now().isoformat(),
            'system_info': {
                'python_version': f"{__import__('sys').version_info.major}.{__import__('sys').version_info.minor}",
                'platform': __import__('platform').platform(),
                'lsl_version': __import__('pylsl').__version__
            },
            'experimental_setup': {
                'expected_streams': self.expected_streams,
                'data_formats': ['csv', 'json'],
                'quality_monitoring': True,
                'auto_reconnection': True
            },
            'data_collection': {
                'output_directory': f"study_data/{self.participant_id}",
                'session_directory': self.session_name,
                'quality_check_interval': 30.0
            }
        }

    def setup_data_collection(self, output_dir: str = "study_data"):
        """Setup data collection components."""
        # Create output directory structure
        participant_dir = Path(output_dir) / self.participant_id
        participant_dir.mkdir(parents=True, exist_ok=True)

        # Create data logger
        self.logger = create_multi_format_logger(
            output_dir=str(participant_dir),
            session_name=self.session_name
        )

        # Create quality assessor
        self.assessor = QualityAssessor(
            check_interval=30.0,
            required_sampling_rate_tolerance=0.1,
            max_missing_data_ratio=0.05
        )

        # Create stream manager
        self.manager = StreamManager(
            target_streams=self.expected_streams,
            auto_discovery=True,
            reconnect_attempts=5
        )

        print(f"✅ Setup complete for participant {self.participant_id}")
        print(f"   Session: {self.session_name}")
        print(f"   Output: {participant_dir}")

    def check_equipment_setup(self) -> dict:
        """Check that all required equipment is streaming."""
        if not self.manager:
            self.setup_data_collection()

        print("🔍 Checking equipment setup...")

        # Discover available streams
        available_streams = self.manager.discover_streams()
        setup_status = {
            'timestamp': datetime.now().isoformat(),
            'available_streams': list(available_streams.keys()),
            'expected_streams': self.expected_streams,
            'missing_streams': [],
            'extra_streams': []
        }

        # Check for missing streams
        for expected in self.expected_streams:
            if expected not in available_streams:
                setup_status['missing_streams'].append(expected)
                print(f"❌ Missing: {expected}")
            else:
                info = available_streams[expected]
                print(f"✅ Found: {expected} ({info.type()}, {info.nominal_srate()} Hz)")

        # Check for extra streams
        for available in available_streams:
            if available not in self.expected_streams:
                setup_status['extra_streams'].append(available)
                print(f"ℹ️  Extra: {available}")

        # Overall status
        if not setup_status['missing_streams']:
            setup_status['status'] = 'complete'
            print("✅ All equipment ready!")
        elif len(setup_status['missing_streams']) < len(self.expected_streams):
            setup_status['status'] = 'partial'
            print("⚠️  Some equipment missing, but can proceed")
        else:
            setup_status['status'] = 'incomplete'
            print("❌ Critical equipment missing")

        return setup_status

    def start_collection(self, duration_minutes: float = None):
        """Start data collection."""
        if not self.manager or not self.logger:
            print("❌ Setup not complete. Call setup_data_collection() first.")
            return

        # Check equipment
        setup_status = self.check_equipment_setup()

        if setup_status['status'] == 'incomplete':
            print("❌ Cannot start collection - critical equipment missing")
            return

        # Connect to streams
        available_streams = self.manager.discover_streams()
        success = self.manager.connect_to_streams(available_streams)

        if not success:
            print("❌ Failed to connect to streams")
            return

        # Start receiving with quality monitoring
        print("
▶️  Starting data collection..."        print(f"   Duration: {'Continuous' if duration_minutes is None else f'{duration_minutes} minutes'}")
        print(f"   Quality checks: Every {self.assessor.check_interval}s")
        print("   Press Ctrl+C to stop early\n")

        success = self.manager.start_receiving(
            data_logger=self.logger,
            quality_assessor=self.assessor
        )

        if not success:
            print("❌ Failed to start data collection")
            return

        # Collection loop
        start_time = time.time()

        try:
            while True:
                elapsed = time.time() - start_time

                # Check if duration limit reached
                if duration_minutes and elapsed > (duration_minutes * 60):
                    print(f"\n⏰ Collection duration ({duration_minutes} min) reached")
                    break

                # Periodic status updates
                if elapsed % 30 < 1:  # Every 30 seconds
                    self._print_status(elapsed)

                time.sleep(1)

        except KeyboardInterrupt:
            print("\n🛑 Collection stopped by user")

        finally:
            self.stop_collection()

    def _print_status(self, elapsed_time: float):
        """Print current collection status."""
        status = self.manager.get_status_summary()
        quality_report = self.assessor.assess_quality(status['stream_info'])

        print("
📊 Status Report:"        print(f"   Time elapsed: {elapsed_time:.1f}s")
        print(f"   Connected streams: {status['connected_streams']}")
        print(f"   Total samples: {status['total_samples_received']:,}")
        print(f"   Overall quality: {quality_report['overall_quality']}")

        # Show quality issues
        if quality_report['issues']:
            print("   Issues:")
            for issue in quality_report['issues'][:3]:  # Show first 3 issues
                print(f"     - {issue}")

    def stop_collection(self):
        """Stop data collection and save everything."""
        print("\n🛑 Stopping collection...")

        if self.manager:
            self.manager.stop_receiving()

        if self.logger:
            self.logger.save_session_summary()
            self.logger.close()

        # Save study metadata
        self._save_study_metadata()

        print("✅ Collection stopped and data saved!")

    def _save_study_metadata(self):
        """Save comprehensive study metadata."""
        if not self.logger:
            return

        # Update metadata with session end info
        self.study_metadata.update({
            'end_time': datetime.now().isoformat(),
            'status': 'completed',
            'total_streams_connected': len(self.manager.streams) if self.manager else 0,
            'total_samples_collected': sum(
                receiver.samples_received
                for receiver in self.manager.streams.values()
            ) if self.manager else 0
        })

        # Save to participant directory
        participant_dir = Path(self.study_metadata['data_collection']['output_directory'])
        metadata_file = participant_dir / f"{self.participant_id}_study_metadata.json"

        with open(metadata_file, 'w') as f:
            json.dump(self.study_metadata, f, indent=2, default=str)

        print(f"📋 Study metadata saved to: {metadata_file}")


def main():
    """Main function with command-line interface."""
    parser = argparse.ArgumentParser(description='Lab Study Data Collector')
    parser.add_argument('participant_id', help='Participant identifier')
    parser.add_argument('--study', '-s', default='default_study',
                       help='Study name')
    parser.add_argument('--duration', '-d', type=float,
                       help='Collection duration in minutes (default: continuous)')
    parser.add_argument('--output', '-o', default='study_data',
                       help='Output directory')
    parser.add_argument('--check-only', action='store_true',
                       help='Only check equipment setup, don\'t start collection')

    args = parser.parse_args()

    # Create collector
    collector = LabStudyCollector(args.participant_id, args.study)

    # Setup
    collector.setup_data_collection(args.output)

    if args.check_only:
        # Only check equipment
        setup_status = collector.check_equipment_setup()
        print("
🔍 Equipment Check Results:"        print(f"   Status: {setup_status['status']}")
        print(f"   Available: {setup_status['available_streams']}")
        if setup_status['missing_streams']:
            print(f"   Missing: {setup_status['missing_streams']}")
        if setup_status['extra_streams']:
            print(f"   Extra: {setup_status['extra_streams']}")
        return

    # Start collection
    collector.start_collection(args.duration)


if __name__ == "__main__":
    main()
