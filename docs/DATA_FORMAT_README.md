# LSL Data Directory

## Overview

This directory contains data recorded from LSL (Lab Streaming Layer) streams during lab sessions. The data is automatically created when you run the LSL Stream Receiver application and start a recording session.

## Directory Structure

```
lsl_data/
├── README.md                              # This file
├── lab_session_YYYYMMDD_HHMM/             # Session directory
│   ├── lsl_data_YYYYMMDD_HHMMSS.csv       # CSV format data
│   ├── lsl_data_YYYYMMDD_HHMMSS.json      # JSON format data
│   └── session_summary.json               # Session metadata
└── lab_session_YYYYMMDD_HHMM/             # Additional sessions
    ├── lsl_data_YYYYMMDD_HHMMSS.csv
    ├── lsl_data_YYYYMMDD_HHMMSS.json
    └── session_summary.json
```

## When Data is Saved

Data is automatically saved when:

1. **Recording is Started**: When you click "Start Recording" in the Streamlit app
2. **Buffer Threshold Reached**: Data is periodically saved based on the buffer size setting
3. **Recording is Stopped**: Final data flush when you click "Stop Recording"
4. **Application Shutdown**: Automatic data flush during graceful shutdown

## Data Formats

### CSV Format (`.csv`)

**Purpose**: Human-readable spreadsheet format for data analysis in Excel, R, Python, etc.

**Structure**:
```csv
timestamp,lsl_timestamp,stream_name,stream_type,sampling_rate,values
2025-09-26 11:39:45.123,123456.789,EEG_Stream,EEG,250.0,"[1.23, 4.56, 7.89, ...]"
2025-09-26 11:39:45.124,123456.790,EEG_Stream,EEG,250.0,"[1.24, 4.57, 7.90, ...]"
```

**Columns**:
- `timestamp`: Local system timestamp (YYYY-MM-DD HH:MM:SS.sss)
- `lsl_timestamp`: LSL stream timestamp (seconds since stream start)
- `stream_name`: Name of the LSL stream
- `stream_type`: Type of the stream (EEG, Gaze, etc.)
- `sampling_rate`: Sampling rate in Hz
- `values`: Array of channel values as JSON string

### JSON Format (`.json`)

**Purpose**: Machine-readable format with rich metadata for programmatic analysis.

**Structure**:
```json
{
  "session_info": {
    "session_name": "lab_session_20250926_1139",
    "start_time": "2025-09-26T11:39:45.123456",
    "end_time": "2025-09-26T11:45:30.789012",
    "duration_seconds": 345.67,
    "streams_recorded": ["EEG_Stream", "Gaze_Stream"]
  },
  "data": [
    {
      "timestamp": "2025-09-26T11:39:45.123456",
      "lsl_timestamp": 123456.789,
      "stream_name": "EEG_Stream",
      "stream_type": "EEG",
      "sampling_rate": 250.0,
      "values": [1.23, 4.56, 7.89, 12.34],
      "sample_index": 1
    },
    {
      "timestamp": "2025-09-26T11:39:45.124456",
      "lsl_timestamp": 123456.790,
      "stream_name": "EEG_Stream",
      "stream_type": "EEG",
      "sampling_rate": 250.0,
      "values": [1.24, 4.57, 7.90, 12.35],
      "sample_index": 2
    }
  ]
}
```

**Fields**:
- `session_info`: Metadata about the recording session
- `data`: Array of sample objects with detailed information

### Session Summary (`session_summary.json`)

**Purpose**: High-level summary of the recording session for quick overview.

**Structure**:
```json
{
  "session_name": "lab_session_20250926_1139",
  "start_time": "2025-09-26T11:39:45.123456",
  "end_time": "2025-09-26T11:45:30.789012",
  "total_samples": 15678,
  "streams": {
    "EEG_Stream": {
      "stream_type": "EEG",
      "sampling_rate": 250.0,
      "channels": 64,
      "samples_recorded": 15678,
      "quality_metrics": {
        "avg_sample_rate": 249.8,
        "dropped_samples": 2,
        "connection_drops": 0
      }
    },
    "Gaze_Stream": {
      "stream_type": "Gaze",
      "sampling_rate": 60.0,
      "channels": 4,
      "samples_recorded": 3456,
      "quality_metrics": {
        "avg_sample_rate": 59.9,
        "dropped_samples": 0,
        "connection_drops": 1
      }
    }
  }
}
```

## Multi-Stream Recording

When multiple LSL streams are recorded simultaneously:

- **Separate files** are created for each stream
- **Session directory** contains all streams from the same recording session
- **Synchronized timing** across all streams using LSL timestamps
- **Individual quality metrics** for each stream

## Data Quality and Validation

### Quality Metrics Tracked:
- **Sample Rate Stability**: Deviation from nominal sampling rate
- **Dropped Samples**: Missing samples in the stream
- **Connection Drops**: Number of connection interruptions
- **Timestamp Continuity**: Gaps in LSL timestamps

### Quality Assessment:
- **Real-time monitoring** during recording
- **Automatic quality checks** every 30 seconds (configurable)
- **Quality reports** saved with session data
- **Visual indicators** in the Streamlit interface

## File Naming Convention

```
lsl_data_YYYYMMDD_HHMMSS.EXT
```

- `YYYYMMDD`: Date of recording (e.g., 20250926)
- `HHMMSS`: Time of recording (e.g., 113945)
- `EXT`: File extension (.csv, .json, .parquet)

## Data Retention and Cleanup

### Automatic Cleanup:
- **Configurable buffer size** (default: 1000 samples per stream)
- **Time-based expiration** for old cached data
- **Disk space monitoring** (future feature)

### Manual Cleanup:
- Delete session directories when no longer needed
- Use standard file system tools for cleanup
- Consider archiving important sessions to external storage

## Integration with Analysis Tools

### Python/Pandas:
```python
import pandas as pd
df = pd.read_csv('lsl_data/lab_session_20250926_1139/lsl_data_20250926_113945.csv')
```

### R:
```r
library(readr)
df <- read_csv('lsl_data/lab_session_20250926_1139/lsl_data_20250926_113945.csv')
```

### MATLAB:
```matlab
data = readtable('lsl_data/lab_session_20250926_1139/lsl_data_20250926_113945.csv');
```

## Privacy and Data Security

### Important Notes:
- **Raw data may contain sensitive information** (EEG, biometric data, etc.)
- **Apply appropriate data protection** measures
- **Consider anonymization** for shared datasets
- **Follow institutional data policies** and ethics guidelines

### Best Practices:
- Store data in encrypted locations when possible
- Use access controls and permissions
- Document data collection protocols
- Maintain data provenance and audit trails

## Troubleshooting

### Common Issues:

1. **Empty Files**: Check if streams were active during recording
2. **Corrupted Data**: Verify stream connections and quality metrics
3. **Missing Timestamps**: Check system clock synchronization
4. **Large Files**: Consider increasing buffer size or save intervals

### Getting Help:
- Check the main project documentation
- Review the Streamlit app logs
- Examine session summary for quality metrics
- Check system resources during recording

---

*This directory is automatically created and managed by the LSL Stream Receiver application. Do not manually edit files while recording is active.*
