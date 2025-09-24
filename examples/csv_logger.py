#!/usr/bin/env python3
"""
CSV Logger Example
=================

This example demonstrates how to log LSL stream data to CSV files
with comprehensive metadata and session management.
"""

import time
import os
from pathlib import Path
from lsl_receiver import StreamManager, DataLogger
from lsl_receiver.data_logger import create_csv_logger


def main():
    """Main CSV logging example."""
    print("📁 CSV Logger Example")
    print("=" * 30)

    # Configuration
    session_name = f"csv_logging_demo_{int(time.time())}"
    output_dir = "csv_demo_data"

    print(f"📂 Session: {session_name}")
    print(f"📂 Output directory: {output_dir}")

    # Create output directory
    Path(output_dir).mkdir(exist_ok=True)

    # Create CSV logger
    logger = create_csv_logger(
        output_dir=output_dir,
        session_name=session_name
    )

    # Create stream manager
    manager = StreamManager()

    try:
        # Discover streams
        print("\n🔍 Discovering streams...")
        stream_infos = manager.discover_streams()

        if not stream_infos:
            print("❌ No streams found")
            return

        print(f"✅ Found streams: {list(stream_infos.keys())}")

        # Connect to streams
        success = manager.connect_to_streams(stream_infos)

        if not success:
            print("❌ Failed to connect")
            return

        # Start receiving with logging
        print("\n▶️  Starting data collection...")
        print("   Data will be saved to CSV files")
        print("   Press Ctrl+C to stop\n")

        success = manager.start_receiving(data_logger=logger)

        if not success:
            print("❌ Failed to start")
            return

        # Monitor for a while
        start_time = time.time()
        duration = 60  # Run for 1 minute

        while time.time() - start_time < duration:
            elapsed = time.time() - start_time

            # Show progress
            if elapsed % 10 < 1:  # Print every 10 seconds
                status = manager.get_status_summary()
                print(f"⏰ {elapsed:.1f}s - Samples: {status['total_samples_received']:,}")

                # Show session info
                session_dir = Path(output_dir) / session_name
                if session_dir.exists():
                    files = list(session_dir.glob("*"))
                    print(f"   📁 Files created: {len(files)}")

                    # Show file sizes
                    for file in files[:3]:  # Show first 3 files
                        size_kb = file.stat().st_size / 1024
                        print(f"      - {file.name}: {size_kb:.1f} KB")

            time.sleep(1)

        print("
⏰ Duration completed!"    except KeyboardInterrupt:
        print("\n🛑 Stopped by user")

    finally:
        # Clean up
        print("\n🧹 Cleaning up...")

        if manager:
            manager.stop_receiving()

        if logger:
            logger.save_session_summary()
            logger.close()

        # Show final results
        session_dir = Path(output_dir) / session_name
        if session_dir.exists():
            print("
📊 Final Results:"            print(f"   📂 Session directory: {session_dir}")

            files = list(session_dir.glob("*"))
            print(f"   📁 Total files: {len(files)}")

            total_size = sum(f.stat().st_size for f in files)
            print(f"   💾 Total size: {total_size / 1024:.1f} KB")

            # Show CSV files
            csv_files = list(session_dir.glob("*.csv"))
            if csv_files:
                print("
📋 CSV Files:"                for csv_file in csv_files:
                    size_kb = csv_file.stat().st_size / 1024
                    line_count = sum(1 for _ in open(csv_file, 'r'))
                    print(f"   - {csv_file.name}: {size_kb:.1f} KB ({line_count:,} lines)")

            # Show metadata
            metadata_files = list(session_dir.glob("*metadata*.json"))
            if metadata_files:
                print("
📋 Metadata Files:"                for meta_file in metadata_files:
                    print(f"   - {meta_file.name}")

        print("✅ CSV logging example completed!")


def advanced_csv_example():
    """Advanced example with custom configuration."""
    print("\n🔧 Advanced CSV Logger Example")
    print("=" * 35)

    # Custom configuration
    config = {
        'session_name': f"advanced_csv_{int(time.time())}",
        'output_dir': "advanced_csv_data",
        'formats': ['csv', 'json'],  # Multiple formats
        'include_metadata': True,
        'quality_metrics': True
    }

    print("Configuration:")
    for key, value in config.items():
        print(f"   {key}: {value}")

    # Create logger with custom settings
    logger = DataLogger(**config)

    # Your stream receiving code here...
    print("📝 Custom logger created with advanced features")

    return logger


if __name__ == "__main__":
    # Run basic example
    main()

    # Optionally run advanced example
    # advanced_csv_example()
