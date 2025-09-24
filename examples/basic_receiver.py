#!/usr/bin/env python3
"""
Basic LSL Stream Receiver Example
================================

This example demonstrates the simplest way to receive data from LSL streams.
Perfect for quick testing and basic data collection.
"""

import time
from lsl_receiver import StreamManager


def main():
    """Main example function."""
    print("🔍 Starting Basic LSL Receiver Example")
    print("=" * 50)

    # Create stream manager with default settings
    manager = StreamManager()

    try:
        # Discover and connect to all available streams
        print("🔍 Discovering available LSL streams...")
        stream_infos = manager.discover_streams()

        if not stream_infos:
            print("❌ No LSL streams found. Make sure your devices are streaming.")
            return

        print(f"✅ Found {len(stream_infos)} streams:")
        for name, info in stream_infos.items():
            print(f"   - {name}: {info.type()} ({info.nominal_srate()} Hz)")

        # Connect to streams
        print("\n🔌 Connecting to streams...")
        success = manager.connect_to_streams(stream_infos)

        if not success:
            print("❌ Failed to connect to any streams")
            return

        # Start receiving data
        print("\n▶️  Starting data reception...")
        print("   Press Ctrl+C to stop")

        success = manager.start_receiving()

        if not success:
            print("❌ Failed to start receiving")
            return

        # Monitor for a while
        start_time = time.time()
        duration = 30  # Run for 30 seconds

        while time.time() - start_time < duration:
            # Get latest data
            latest_data = manager.get_latest_data()

            # Print status every 5 seconds
            if int(time.time() - start_time) % 5 == 0:
                status = manager.get_status_summary()
                print(f"\n📊 Status at {time.time() - start_time:.1f}s:")
                print(f"   - Connected streams: {status['connected_streams']}")
                print(f"   - Total samples: {status['total_samples_received']:,}")
                print(f"   - Buffered samples: {sum(status['latest_data_count'].values()):,}")

                # Show latest sample from each stream
                for stream_name, samples in latest_data.items():
                    if samples:
                        latest = samples[-1]
                        values = latest.get('values', [])
                        print(f"   - {stream_name}: {[f'{v:.3f}' for v in values[:3]]}")

            time.sleep(0.1)

        print("⏰ Time's up! Stopping..."    
    except KeyboardInterrupt:
        print("\n🛑 Stopped by user")

    finally:
        # Clean up
        print("\n🧹 Cleaning up...")
        manager.stop_receiving()
        print("✅ Done!")


if __name__ == "__main__":
    main()
