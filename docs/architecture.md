# LSL Stream Receiver Architecture Guide

This comprehensive guide details the system architecture, design decisions, and technical implementation of the LSL Stream Receiver.

## 📋 Table of Contents

- [System Overview](#-system-overview)
- [Design Principles](#-design-principles)
- [Component Architecture](#-component-architecture)
- [Data Flow](#-data-flow)
- [Concurrency Model](#-concurrency-model)
- [Error Handling](#-error-handling)
- [Quality Assurance](#-quality-assurance)
- [Performance Characteristics](#-performance-characteristics)
- [Scalability Considerations](#-scalability-considerations)

## 🎯 System Overview

### Purpose and Scope

The LSL Stream Receiver is designed to provide a robust, research-grade solution for receiving, processing, and logging data from multiple Lab Streaming Layer (LSL) streams simultaneously. The system is optimized for:

- **Real-time data acquisition** from physiological sensors, behavioral devices, and experimental equipment
- **Multi-modal data synchronization** across different sampling rates and latencies
- **Quality assurance** with built-in signal quality monitoring and validation
- **Flexible data export** supporting multiple formats for analysis pipelines
- **Web-based monitoring** for real-time experiment oversight

### Target Use Cases

1. **Neurophysiological Research**: EEG, fMRI, MEG data collection
2. **Psychophysiological Studies**: GSR, ECG, EMG, eye tracking
3. **Behavioral Experiments**: Response times, stimuli presentation
4. **Multi-modal Integration**: Combining multiple data streams
5. **Real-time Biofeedback**: Live signal processing and feedback

### System Boundaries

```
┌─────────────────────────────────────────────────────────────┐
│                    LSL Stream Receiver                      │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐          │
│  │StreamManager│  │ DataLogger  │  │QualityAssess│          │
│  │             │  │             │  │             │          │
│  │- Discovery  │  │- CSV/JSON   │  │- Sampling   │          │
│  │- Connection │  │- Metadata   │  │- Quality    │          │
│  │- Buffering  │  │- Export     │  │- Alerts     │          │
│  └─────────────┘  └─────────────┘  └─────────────┘          │
├─────────────────────────────────────────────────────────────┤
│  External Systems                                           │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐          │
│  │  LSL Streams│  │   Database  │  │Analysis Tools│          │
│  │             │  │             │  │             │          │
│  │- EEG Amp   │  │- PostgreSQL │  │- MATLAB     │          │
│  │- ECG Mon.  │  │- MongoDB    │  │- Python     │          │
│  │- Eye Track │  │- CSV Files  │  │- R          │          │
│  └─────────────┘  └─────────────┘  └─────────────┘          │
└─────────────────────────────────────────────────────────────┘
```

## 🏗️ Design Principles

### 1. Modularity and Separation of Concerns

The system is designed with clear separation between components:

```
Core Library (lsl_receiver/)
├── StreamManager       # Stream discovery and management
├── DataLogger         # Data storage and export
├── QualityAssessor    # Quality monitoring and validation
├── StreamReceiver     # Individual stream handling
└── Synchronizer       # Cross-stream synchronization

Web Interface (streamlit_app/)
├── Dashboard          # Real-time monitoring
├── StreamView         # Individual stream details
├── DataManager        # Data export and management
└── Settings           # Configuration interface
```

### 2. Thread Safety and Concurrency

- **Immutable data structures** for thread-safe operations
- **Queue-based communication** between components
- **Atomic operations** for critical sections
- **Lock-free algorithms** where performance-critical

### 3. Quality-First Approach

- **Built-in quality monitoring** for all data streams
- **Comprehensive error handling** with graceful degradation
- **Data validation** at multiple levels
- **Audit trails** for troubleshooting

### 4. Extensibility and Plugin Architecture

- **Plugin interface** for new stream types
- **Format plugins** for additional export formats
- **Processing plugins** for custom data transformations
- **Integration plugins** for external systems

### 5. Performance Optimization

- **Memory-efficient buffering** with circular buffers
- **Lazy evaluation** for expensive operations
- **Caching strategies** for metadata and configurations
- **Batch processing** for I/O operations

## 🏛️ Component Architecture

### Core Components

#### StreamManager
```python
class StreamManager:
    """Central coordinator for multiple LSL streams."""

    def __init__(self):
        self.streams: Dict[str, StreamReceiver] = {}
        self.synchronizer: StreamSynchronizer = StreamSynchronizer()
        self.quality_monitor: QualityMonitor = QualityMonitor()
        self.event_bus: EventBus = EventBus()

    async def discover_streams(self) -> List[StreamInfo]:
        """Discover available LSL streams."""

    async def connect_streams(self, stream_infos: List[StreamInfo]):
        """Connect to discovered streams."""

    async def start_receiving(self):
        """Start data reception from all streams."""

    def get_synchronized_data(self) -> Dict[str, np.ndarray]:
        """Get temporally synchronized data from all streams."""
```

#### DataLogger
```python
class DataLogger:
    """Handles data storage and export with metadata."""

    def __init__(self, config: LoggerConfig):
        self.config = config
        self.session_manager = SessionManager()
        self.formatters = {
            'csv': CSVFormatter(),
            'json': JSONFormatter(),
            'parquet': ParquetFormatter()
        }

    async def log_data(self, data: Dict[str, np.ndarray]):
        """Log data to all configured formats."""

    async def export_session(self, session_id: str, format: str):
        """Export specific session data."""
```

#### QualityAssessor
```python
class QualityAssessor:
    """Monitors and assesses data quality in real-time."""

    def __init__(self, config: QualityConfig):
        self.config = config
        self.metrics_calculator = MetricsCalculator()
        self.alert_system = AlertSystem()

    async def assess_stream_quality(self, stream: StreamReceiver) -> QualityReport:
        """Assess quality of individual stream."""

    async def generate_quality_report(self) -> QualityReport:
        """Generate comprehensive quality report."""
```

### Supporting Components

#### StreamReceiver
```python
class StreamReceiver:
    """Handles individual LSL stream connection and data reception."""

    def __init__(self, stream_info: StreamInfo):
        self.stream_info = stream_info
        self.inlet: StreamInlet = None
        self.buffer: CircularBuffer = CircularBuffer()
        self.connection_manager = ConnectionManager()

    async def connect(self) -> bool:
        """Establish connection to LSL stream."""

    async def receive_data(self) -> np.ndarray:
        """Receive data from connected stream."""

    def get_quality_metrics(self) -> Dict[str, float]:
        """Get quality metrics for this stream."""
```

#### StreamSynchronizer
```python
class StreamSynchronizer:
    """Synchronizes data from multiple streams temporally."""

    def __init__(self):
        self.reference_clock = ReferenceClock()
        self.offset_calculator = OffsetCalculator()
        self.interpolator = TimeInterpolator()

    def synchronize(self, streams_data: Dict[str, np.ndarray]) -> Dict[str, np.ndarray]:
        """Synchronize data from multiple streams."""

    def calculate_offsets(self, timestamps: Dict[str, np.ndarray]) -> Dict[str, float]:
        """Calculate temporal offsets between streams."""
```

## 🔄 Data Flow

### 1. Stream Discovery Phase

```
┌─────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ LSL Network │───▶│ Stream Resolver │───▶│ Metadata Extract│
│             │    │                 │    │                 │
│ - Broadcast │    │ - Network scan  │    │ - Stream info   │
│ - Multicast │    │ - Service disc. │    │ - Channel info  │
│ - Direct    │    │ - Timeout       │    │ - Sampling rate │
└─────────────┘    └─────────────────┘    └─────────────────┘
```

### 2. Connection Establishment

```
┌─────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ Stream Info │───▶│ Connection Mgr  │───▶│ Stream Receiver │
│             │    │                 │    │                 │
│ - Validate  │    │ - Create inlet  │    │ - Buffer setup  │
│ - Filter    │    │ - Test connect. │    │ - Quality init  │
│ - Prioritize│    │ - Configure     │    │ - Monitor setup │
└─────────────┘    └─────────────────┘    └─────────────────┘
```

### 3. Data Reception Pipeline

```
┌─────────────┐    ┌─────────────────┐    ┌─────────────────┐
│LSL Stream   │───▶│ Stream Receiver │───▶│ Data Buffer     │
│             │    │                 │    │                 │
│ - Raw data  │    │ - Pull samples  │    │ - Circular buf  │
│ - Timestamps│    │ - Error handle  │    │ - Thread-safe   │
│ - Metadata  │    │ - Rate limit    │    │ - Overflow prot │
└─────────────┘    └─────────────────┘    └─────────────────┘
```

### 4. Processing and Quality Assessment

```
┌─────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ Data Buffer │───▶│ Quality Assessor│───▶│ Synchronizer    │
│             │    │                 │    │                 │
│ - Multiple  │    │ - Rate check    │    │ - Temporal      │
│ - Streams   │    │ - Signal qual   │    │ - Alignment     │
│ - Async     │    │ - Missing data  │    │ - Interpolation │
└─────────────┘    └─────────────────┘    └─────────────────┘
```

### 5. Storage and Export

```
┌─────────────┐    ┌─────────────────┐    ┌─────────────────┐
│Synchronized │───▶│ Data Logger     │───▶│ Export Formats  │
│ Data        │    │                 │    │                 │
│             │    │ - Format conv.  │    │ - CSV           │
│ - Quality   │    │ - Metadata add  │    │ - JSON          │
│ - Metadata  │    │ - Session mgmt  │    │ - Parquet       │
└─────────────┘    └─────────────────┘    └─────────────────┘
```

## 🔄 Concurrency Model

### Thread Architecture

```
Main Thread (UI/Control)
    ├── Stream Discovery Thread
    ├── Data Reception Thread Pool
    ├── Quality Monitoring Thread
    └── Export Thread Pool

Background Threads
    ├── Connection Management
    ├── Buffer Management
    ├── Quality Assessment
    └── Data Export
```

### Async/Await Pattern

```python
class AsyncStreamManager:
    """Asynchronous stream management with proper concurrency."""

    async def manage_streams(self):
        """Main stream management loop."""
        # Concurrent stream discovery
        discovery_tasks = [
            self.discover_lsl_streams(),
            self.discover_network_streams(),
            self.discover_local_streams()
        ]

        stream_infos = await asyncio.gather(*discovery_tasks)
        stream_infos = [item for sublist in stream_infos for item in sublist]

        # Concurrent connection establishment
        connection_tasks = [
            self.connect_stream(info) for info in stream_infos
        ]

        connections = await asyncio.gather(*connection_tasks, return_exceptions=True)

        # Start data reception
        await self.start_reception()
```

### Thread Safety Mechanisms

#### 1. Immutable Data Structures
```python
@dataclass(frozen=True)
class StreamInfo:
    """Immutable stream information."""
    name: str
    stream_type: str
    sampling_rate: float
    channels: int
    data_format: str

    def __hash__(self):
        return hash((self.name, self.stream_type, self.sampling_rate))
```

#### 2. Thread-Safe Collections
```python
class ThreadSafeStreamDict:
    """Thread-safe dictionary for stream management."""

    def __init__(self):
        self._streams: Dict[str, StreamReceiver] = {}
        self._lock = asyncio.Lock()

    async def add_stream(self, name: str, receiver: StreamReceiver):
        async with self._lock:
            self._streams[name] = receiver

    async def get_stream(self, name: str) -> StreamReceiver:
        async with self._lock:
            return self._streams.get(name)

    async def remove_stream(self, name: str):
        async with self._lock:
            self._streams.pop(name, None)
```

#### 3. Queue-Based Communication
```python
class DataQueue:
    """Queue-based data transfer between threads."""

    def __init__(self, max_size: int = 1000):
        self.queue = asyncio.Queue(max_size)
        self.closed = False

    async def put(self, data: Dict[str, np.ndarray]):
        if not self.closed:
            await self.queue.put(data)

    async def get(self) -> Dict[str, np.ndarray]:
        return await self.queue.get()

    def close(self):
        self.closed = True
```

## ⚠️ Error Handling

### Error Classification

1. **Network Errors**
   - Connection timeouts
   - Network disconnections
   - DNS resolution failures

2. **Stream Errors**
   - Invalid stream formats
   - Sampling rate mismatches
   - Channel count changes

3. **Data Errors**
   - Corrupted samples
   - Missing timestamps
   - Out-of-range values

4. **System Errors**
   - Memory exhaustion
   - Disk space issues
   - Permission errors

### Error Recovery Strategies

#### 1. Exponential Backoff
```python
class ExponentialBackoff:
    """Exponential backoff for connection retries."""

    def __init__(self, initial_delay: float = 1.0, max_delay: float = 60.0):
        self.initial_delay = initial_delay
        self.max_delay = max_delay
        self.current_delay = initial_delay
        self.attempts = 0

    async def wait(self):
        """Wait with exponential backoff."""
        await asyncio.sleep(self.current_delay)
        self.attempts += 1
        self.current_delay = min(
            self.initial_delay * (2 ** self.attempts),
            self.max_delay
        )

    def reset(self):
        """Reset backoff state."""
        self.current_delay = self.initial_delay
        self.attempts = 0
```

#### 2. Circuit Breaker Pattern
```python
class CircuitBreaker:
    """Circuit breaker for failing connections."""

    def __init__(self, failure_threshold: int = 5, timeout: float = 60.0):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = 'CLOSED'  # CLOSED, OPEN, HALF_OPEN

    async def call(self, func, *args, **kwargs):
        """Execute function with circuit breaker protection."""
        if self.state == 'OPEN':
            if time.time() - self.last_failure_time > self.timeout:
                self.state = 'HALF_OPEN'
            else:
                raise CircuitOpenException("Circuit breaker is OPEN")

        try:
            result = await func(*args, **kwargs)
            self._on_success()
            return result

        except Exception as e:
            self._on_failure()
            raise e

    def _on_success(self):
        """Handle successful execution."""
        self.failure_count = 0
        self.state = 'CLOSED'

    def _on_failure(self):
        """Handle failed execution."""
        self.failure_count += 1
        self.last_failure_time = time.time()

        if self.failure_count >= self.failure_threshold:
            self.state = 'OPEN'
```

#### 3. Graceful Degradation
```python
class GracefulDegradation:
    """Graceful degradation for partial failures."""

    def __init__(self, essential_streams: List[str]):
        self.essential_streams = set(essential_streams)
        self.available_streams = set()

    async def handle_stream_failure(self, stream_name: str):
        """Handle failure of individual stream."""
        if stream_name in self.essential_streams:
            # Essential stream failed - consider system degraded
            raise CriticalStreamFailure(f"Essential stream {stream_name} failed")

        # Non-essential stream - continue with reduced functionality
        logging.warning(f"Non-essential stream {stream_name} failed - continuing")

    async def can_continue(self) -> bool:
        """Check if system can continue operating."""
        return bool(self.essential_streams & self.available_streams)
```

## ✅ Quality Assurance

### Quality Metrics

#### 1. Sampling Rate Stability
```python
class SamplingRateMonitor:
    """Monitors sampling rate stability."""

    def __init__(self, nominal_rate: float, tolerance: float = 0.05):
        self.nominal_rate = nominal_rate
        self.tolerance = tolerance
        self.rate_history = []
        self.timestamp_history = []

    def add_sample(self, timestamp: float):
        """Add sample timestamp for rate calculation."""
        if self.timestamp_history:
            interval = timestamp - self.timestamp_history[-1]
            rate = 1.0 / interval if interval > 0 else 0.0
            self.rate_history.append(rate)

        self.timestamp_history.append(timestamp)

    def get_rate_deviation(self) -> float:
        """Get deviation from nominal sampling rate."""
        if not self.rate_history:
            return 0.0

        avg_rate = sum(self.rate_history) / len(self.rate_history)
        return abs(avg_rate - self.nominal_rate) / self.nominal_rate
```

#### 2. Signal Quality Metrics
```python
class SignalQualityMetrics:
    """Comprehensive signal quality assessment."""

    def __init__(self, signal_type: str):
        self.signal_type = signal_type
        self.metrics = {
            'snr': SignalToNoiseRatio(),
            'artifacts': ArtifactDetector(),
            'saturation': SaturationDetector(),
            'baseline_drift': DriftDetector()
        }

    def assess_quality(self, data: np.ndarray) -> Dict[str, float]:
        """Assess overall signal quality."""
        quality_scores = {}

        for name, metric in self.metrics.items():
            try:
                quality_scores[name] = metric.calculate(data)
            except Exception as e:
                logging.error(f"Error calculating {name}: {e}")
                quality_scores[name] = 0.0

        # Combine metrics based on signal type
        weights = self._get_metric_weights()
        overall_quality = sum(
            score * weight for score, weight in zip(quality_scores.values(), weights)
        )

        return {
            **quality_scores,
            'overall': overall_quality
        }

    def _get_metric_weights(self) -> List[float]:
        """Get weights for different signal types."""
        if self.signal_type == 'EEG':
            return [0.4, 0.3, 0.2, 0.1]  # SNR, Artifacts, Saturation, Drift
        elif self.signal_type == 'ECG':
            return [0.3, 0.4, 0.2, 0.1]
        else:
            return [0.25, 0.25, 0.25, 0.25]  # Equal weighting
```

#### 3. Connection Stability
```python
class ConnectionStabilityMonitor:
    """Monitors connection stability and reliability."""

    def __init__(self, window_size: int = 100):
        self.window_size = window_size
        self.connection_events = []
        self.disconnection_events = []
        self.reconnection_attempts = []

    def log_connection_event(self, timestamp: float, success: bool):
        """Log connection event."""
        if success:
            self.connection_events.append(timestamp)
        else:
            self.disconnection_events.append(timestamp)

        # Keep only recent events
        cutoff = timestamp - (self.window_size * 0.1)  # Last window
        self.connection_events = [t for t in self.connection_events if t > cutoff]
        self.disconnection_events = [t for t in self.disconnection_events if t > cutoff]

    def get_stability_score(self) -> float:
        """Calculate connection stability score."""
        total_events = len(self.connection_events) + len(self.disconnection_events)

        if total_events == 0:
            return 1.0  # Perfect stability

        successful_connections = len(self.connection_events)
        stability = successful_connections / total_events

        # Penalize frequent disconnections
        disconnection_rate = len(self.disconnection_events) / max(total_events, 1)
        stability_penalty = min(disconnection_rate * 0.5, 0.5)

        return max(0.0, stability - stability_penalty)
```

### Quality Thresholds and Alerts

```python
class QualityAlertSystem:
    """System for quality-based alerting."""

    def __init__(self):
        self.alert_rules = {
            'critical': QualityAlertRule(threshold=0.3, severity='critical'),
            'warning': QualityAlertRule(threshold=0.7, severity='warning'),
            'info': QualityAlertRule(threshold=0.9, severity='info')
        }
        self.active_alerts = []

    async def check_quality_alerts(self, quality_report: Dict[str, float]):
        """Check quality against alert thresholds."""
        overall_quality = quality_report.get('overall', 1.0)

        for rule in self.alert_rules.values():
            if rule.should_trigger(overall_quality):
                await self._trigger_alert(rule, overall_quality)

    async def _trigger_alert(self, rule: QualityAlertRule, quality: float):
        """Trigger quality alert."""
        alert = QualityAlert(
            rule=rule,
            quality_score=quality,
            timestamp=time.time()
        )

        self.active_alerts.append(alert)

        # Send notifications
        await self._send_notifications(alert)
```

## 📈 Performance Characteristics

### Benchmarking Results

#### Stream Reception Performance
```
Configuration: 4 streams @ 500Hz each, 32 channels per stream
System: Intel i7-8700K, 32GB RAM, SSD storage

Metric                  Value
──────────────────────  ─────
CPU Usage               15-25%
Memory Usage            200-400MB
Throughput              50k samples/sec
Latency (mean)          2.1ms
Latency (p95)           4.8ms
Buffer Overflow Rate    <0.01%
Quality Score           0.95+
```

#### Data Export Performance
```
Format      Write Speed     File Size    Compression
──────      ───────────     ─────────    ───────────
CSV         120 MB/s        1.2 GB/min   None
JSON        80 MB/s         1.4 GB/min   None
Parquet     95 MB/s         0.8 GB/min   40%
HDF5        110 MB/s        0.9 GB/min   35%
```

### Scalability Limits

#### Concurrent Streams
- **Recommended**: 8-12 streams (depends on sampling rates)
- **Maximum**: 20-25 streams (with appropriate hardware)
- **Limiting factors**: CPU, memory bandwidth, disk I/O

#### Sampling Rates
- **EEG (500Hz)**: Up to 8 streams simultaneously
- **ECG (250Hz)**: Up to 12 streams simultaneously
- **Eye Tracking (60Hz)**: Up to 20 streams simultaneously
- **High-frequency (1000Hz+)**: 4-6 streams maximum

#### Data Volume
- **Sustained**: 100MB/minute (multiple formats)
- **Peak**: 200MB/minute (short bursts)
- **Storage**: 50GB/hour (compressed formats)

### Resource Utilization

#### Memory Usage Patterns
```python
# Typical memory allocation
base_memory = 50MB         # Core application
per_stream = 20MB          # Buffer + metadata
quality_monitoring = 10MB  # Quality history
export_buffers = 30MB      # Export staging

total_memory = base_memory + (n_streams * per_stream) + quality_monitoring + export_buffers
```

#### CPU Usage Distribution
```
Stream Reception:     35%
Quality Assessment:   25%
Data Processing:      20%
Export/Storage:       15%
UI/Monitoring:         5%
```

## 🔄 Scalability Considerations

### Horizontal Scaling

#### Multi-Process Architecture
```python
class MultiProcessManager:
    """Manage multiple LSL receiver processes."""

    def __init__(self, n_processes: int = 4):
        self.n_processes = n_processes
        self.process_pool = []
        self.load_balancer = LoadBalancer()

    async def start_processes(self):
        """Start multiple receiver processes."""
        for i in range(self.n_processes):
            process = LSLReceiverProcess(process_id=i)
            await process.start()
            self.process_pool.append(process)

    async def distribute_load(self, stream_configs: List[StreamConfig]):
        """Distribute stream load across processes."""
        assignments = self.load_balancer.distribute(stream_configs)

        for process_id, streams in assignments.items():
            await self.process_pool[process_id].assign_streams(streams)
```

#### Distributed Data Collection
```python
class DistributedCollector:
    """Collect data from multiple distributed receivers."""

    def __init__(self, receivers: List[str]):
        self.receivers = receivers
        self.consolidator = DataConsolidator()
        self.synchronizer = DistributedSynchronizer()

    async def collect_distributed_data(self) -> Dict[str, np.ndarray]:
        """Collect and synchronize data from distributed receivers."""
        # Collect data from all receivers
        data_tasks = [
            self._collect_from_receiver(receiver)
            for receiver in self.receivers
        ]

        receiver_data = await asyncio.gather(*data_tasks)

        # Synchronize across receivers
        synchronized_data = self.synchronizer.synchronize(receiver_data)

        # Consolidate into unified dataset
        return self.consolidator.consolidate(synchronized_data)
```

### Vertical Scaling

#### Memory Pool Optimization
```python
class MemoryPoolManager:
    """Manage memory pools for efficient allocation."""

    def __init__(self):
        self.pools = {
            'small': MemoryPool(size=1024, block_size=64),
            'medium': MemoryPool(size=4096, block_size=256),
            'large': MemoryPool(size=16384, block_size=1024)
        }

    def allocate_buffer(self, size: int, stream_type: str) -> np.ndarray:
        """Allocate buffer from appropriate pool."""
        pool_name = self._select_pool(size, stream_type)
        return self.pools[pool_name].allocate(size)

    def _select_pool(self, size: int, stream_type: str) -> str:
        """Select appropriate memory pool."""
        if stream_type in ['EEG', 'MEG']:
            return 'large'
        elif size > 1024:
            return 'medium'
        else:
            return 'small'
```

#### CPU Optimization Strategies
```python
class CPUOptimizer:
    """CPU optimization for high-performance scenarios."""

    def __init__(self):
        self.vectorized_ops = VectorizedOperations()
        self.parallel_processing = ParallelProcessor()
        self.cache_manager = ComputationCache()

    def optimize_processing(self, data: np.ndarray, operations: List[str]):
        """Optimize data processing pipeline."""
        # Check cache first
        cache_key = self._compute_cache_key(data, operations)
        if self.cache_manager.has(cache_key):
            return self.cache_manager.get(cache_key)

        # Apply vectorized operations
        optimized_data = data
        for operation in operations:
            if operation in self.vectorized_ops.supported_ops:
                optimized_data = self.vectorized_ops.apply(operation, optimized_data)
            else:
                # Fall back to parallel processing
                optimized_data = self.parallel_processing.apply(operation, optimized_data)

        # Cache result
        self.cache_manager.put(cache_key, optimized_data)

        return optimized_data
```

### Load Balancing

#### Adaptive Load Balancing
```python
class AdaptiveLoadBalancer:
    """Adaptive load balancing based on system metrics."""

    def __init__(self):
        self.system_monitor = SystemMonitor()
        self.load_metrics = LoadMetrics()
        self.balancer = LoadBalancer()

    async def balance_load(self, streams: List[StreamConfig]) -> Dict[int, List[StreamConfig]]:
        """Balance stream load across available resources."""
        # Monitor current system state
        system_state = await self.system_monitor.get_state()

        # Calculate optimal distribution
        optimal_distribution = self._calculate_optimal_distribution(
            streams, system_state
        )

        # Apply balancing
        return self.balancer.distribute(optimal_distribution)

    def _calculate_optimal_distribution(
        self,
        streams: List[StreamConfig],
        system_state: SystemState
    ) -> Dict[int, List[StreamConfig]]:
        """Calculate optimal stream distribution."""
        # Consider CPU cores, memory, network bandwidth
        available_resources = system_state.available_resources
        stream_requirements = [self._calculate_stream_requirements(s) for s in streams]

        return self._optimize_distribution(stream_requirements, available_resources)
```

#### Resource-Aware Scheduling
```python
class ResourceAwareScheduler:
    """Schedule stream processing based on resource availability."""

    def __init__(self):
        self.resource_monitor = ResourceMonitor()
        self.priority_queue = PriorityQueue()
        self.scheduling_policy = SchedulingPolicy()

    async def schedule_processing(self, tasks: List[ProcessingTask]):
        """Schedule processing tasks based on resource availability."""
        # Assess resource availability
        resources = await self.resource_monitor.get_available_resources()

        # Prioritize tasks
        prioritized_tasks = self.priority_queue.prioritize(tasks)

        # Schedule based on policy
        schedule = self.scheduling_policy.schedule(prioritized_tasks, resources)

        return schedule
```

## 🔒 Security Considerations

### Data Protection
- **Encryption at rest** for sensitive research data
- **Access control** for data export and sharing
- **Audit logging** for data access and modifications

### Network Security
- **TLS encryption** for network communications
- **Authentication** for multi-user environments
- **Firewall configuration** for LSL traffic

### Privacy Compliance
- **GDPR compliance** for participant data
- **HIPAA compliance** for medical data
- **Data anonymization** tools and procedures

---

*This architecture guide is maintained by the lab's technical team. For updates or corrections, please create an issue or submit a pull request.*
