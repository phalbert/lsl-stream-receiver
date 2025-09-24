#!/usr/bin/env python3
"""
Real-Time Plotter Example
========================

This example demonstrates real-time plotting of LSL stream data
using matplotlib for live visualization.
"""

import time
import threading
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from collections import defaultdict
from lsl_receiver import StreamManager


class RealTimePlotter:
    """Real-time plotting of LSL stream data."""

    def __init__(self, max_points: int = 1000):
        self.max_points = max_points
        self.stream_data = defaultdict(lambda: {'times': [], 'values': [], 'channels': 0})

        # Setup matplotlib
        self.fig, self.axes = plt.subplots(2, 2, figsize=(12, 8))
        self.fig.suptitle('LSL Stream Real-Time Data', fontsize=16)
        self.lines = {}
        self.setup_plots()

        # Animation
        self.animation = FuncAnimation(self.fig, self.update_plots, interval=100, blit=False)

    def setup_plots(self):
        """Setup the plot axes and lines."""
        self.axes = self.axes.flatten()

        # Plot configuration
        colors = ['blue', 'red', 'green', 'orange', 'purple', 'brown', 'pink', 'gray']
        titles = ['Stream 1', 'Stream 2', 'Stream 3', 'Stream 4']

        for i, ax in enumerate(self.axes):
            ax.set_title(titles[i])
            ax.set_xlabel('Time (s)')
            ax.set_ylabel('Value')
            ax.grid(True, alpha=0.3)

            # Create line for each possible channel
            self.lines[i] = []
            for j in range(4):  # Max 4 channels per plot
                line, = ax.plot([], [], color=colors[j % len(colors)], label=f'Ch{j+1}')
                self.lines[i].append(line)

            ax.legend()

    def update_stream_data(self, latest_data: dict):
        """Update data for plotting."""
        current_time = time.time()

        for stream_name, samples in latest_data.items():
            if not samples:
                continue

            # Get or create data arrays for this stream
            stream_data = self.stream_data[stream_name]

            # Update channel count if needed
            latest_sample = samples[-1]
            values = latest_sample.get('values', [])
            n_channels = len(values)

            if stream_data['channels'] != n_channels:
                stream_data['channels'] = n_channels
                stream_data['times'] = []
                stream_data['values'] = [[] for _ in range(n_channels)]

            # Add new data
            for sample in samples:
                sample_time = sample.get('timestamp', current_time)
                relative_time = sample_time - current_time  # Negative for recent data

                values = sample.get('values', [])
                stream_data['times'].append(relative_time)

                for i, value in enumerate(values):
                    if i < len(stream_data['values']):
                        stream_data['values'][i].append(value)

            # Keep only recent points
            if len(stream_data['times']) > self.max_points:
                keep_points = self.max_points
                stream_data['times'] = stream_data['times'][-keep_points:]

                for i in range(len(stream_data['values'])):
                    stream_data['values'][i] = stream_data['values'][i][-keep_points:]

    def update_plots(self, frame):
        """Update plot data for animation."""
        current_time = time.time()

        # Update each subplot
        for i, ax in enumerate(self.axes):
            ax.clear()
            ax.set_title(f'Stream {i+1}')
            ax.set_xlabel('Time (s)')
            ax.set_ylabel('Value')
            ax.grid(True, alpha=0.3)

            # Plot data for streams that have data
            stream_index = 0
            for stream_name, stream_data in list(self.stream_data.items())[:4]:  # Max 4 streams
                if stream_index >= i * 2 and stream_index < (i + 1) * 2:  # 2 streams per subplot
                    times = np.array(stream_data['times'])
                    subplot_index = stream_index % 2

                    # Plot each channel
                    colors = ['blue', 'red', 'green', 'orange']
                    for ch_idx, values in enumerate(stream_data['values'][:4]):  # Max 4 channels
                        if values:
                            ax.plot(times, values,
                                   color=colors[ch_idx],
                                   label=f'{stream_name}-Ch{ch_idx+1}')

                    if stream_data['values'] and any(stream_data['values']):
                        ax.legend()

                stream_index += 1

        return self.axes

    def show(self):
        """Show the plot window."""
        plt.tight_layout()
        plt.show()

    def save_animation(self, filename: str, duration: int = 10):
        """Save animation as video file."""
        print(f"📹 Saving animation to {filename}...")
        # Note: This would require ffmpeg or similar backend
        # For now, just print the message
        print("💡 To save animations, install matplotlib animation writers:")
        print("   pip install ffmpeg-python")


def main():
    """Main real-time plotting example."""
    print("📈 Real-Time LSL Plotter")
    print("=" * 30)

    # Create stream manager
    manager = StreamManager()
    plotter = RealTimePlotter(max_points=500)

    try:
        # Discover and connect to streams
        print("\n🔍 Discovering streams...")
        stream_infos = manager.discover_streams()

        if not stream_infos:
            print("❌ No streams found")
            return

        print(f"✅ Found {len(stream_infos)} streams:")
        for name, info in stream_infos.items():
            print(f"   - {name}: {info.type()} ({info.nominal_srate()} Hz)")

        success = manager.connect_to_streams(stream_infos)

        if not success:
            print("❌ Failed to connect")
            return

        # Start receiving
        print("\n▶️  Starting real-time plotting...")
        print("   Close the plot window or press Ctrl+C to stop")

        success = manager.start_receiving()

        if not success:
            print("❌ Failed to start")
            return

        # Start plotting in separate thread
        plot_thread = threading.Thread(target=plotter.show, daemon=True)
        plot_thread.start()

        # Monitor and update plots
        start_time = time.time()
        duration = 60  # Run for 1 minute

        while time.time() - start_time < duration:
            try:
                # Get latest data
                latest_data = manager.get_latest_data()

                # Update plot data
                plotter.update_stream_data(latest_data)

                # Small delay to prevent excessive CPU usage
                time.sleep(0.1)

            except KeyboardInterrupt:
                break

        print("
⏰ Time's up!"    except KeyboardInterrupt:
        print("\n🛑 Stopped by user")

    finally:
        # Clean up
        print("\n🧹 Cleaning up...")
        if manager:
            manager.stop_receiving()
        print("✅ Done!")


def simple_monitoring_example():
    """Simple monitoring without full plotting."""
    print("\n📊 Simple Monitoring Example")
    print("=" * 30)

    manager = StreamManager()

    try:
        # Connect to streams
        stream_infos = manager.discover_streams()

        if not stream_infos:
            print("❌ No streams found")
            return

        manager.connect_to_streams(stream_infos)
        manager.start_receiving()

        print("\n📊 Monitoring streams...")
        print("Press Ctrl+C to stop\n")

        # Simple monitoring loop
        start_time = time.time()

        while True:
            elapsed = time.time() - start_time

            # Print status every 5 seconds
            if elapsed % 5 < 0.1:
                status = manager.get_status_summary()
                latest_data = manager.get_latest_data()

                print(f"⏰ {elapsed:.1f}s - Streams: {status['connected_streams']}, "
                      f"Samples: {status['total_samples_received']:,}")

                # Show latest values
                for stream_name, samples in latest_data.items():
                    if samples:
                        latest = samples[-1]
                        values = latest.get('values', [])
                        print(f"   {stream_name}: {[f'{v:.3f}' for v in values[:3]]}")

            time.sleep(0.5)

    except KeyboardInterrupt:
        print("\n🛑 Stopped")
    finally:
        manager.stop_receiving()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Real-time LSL plotting')
    parser.add_argument('--simple', action='store_true',
                       help='Run simple monitoring instead of full plotting')

    args = parser.parse_args()

    if args.simple:
        simple_monitoring_example()
    else:
        main()
