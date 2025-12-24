# LSL Stream Receiver - Modular Architecture

## Overview

This directory contains the refactored LSL Stream Receiver application with a **modular architecture** designed for maintainability, scalability, and team collaboration.

## Architecture

```
streamlit_app/
├── __init__.py              # Package initialization
├── app_new.py              # New modular main application (RECOMMENDED)
├── app.py                  # Original monolithic version (DEPRECATED)
├── README.md               # This file
│
├── core/                   # Core application logic
│   ├── __init__.py
│   └── app.py              # Main interface orchestration
│
├── tabs/                   # Individual tab implementations
│   ├── __init__.py
│   ├── dashboard.py        # Dashboard tab
│   ├── streams.py          # Streams management tab
│   ├── graphs.py           # Real-time graphs tab
│   ├── data.py             # Data management tab
│   └── settings.py         # Settings tab
│
└── utils/                  # Shared utilities
    ├── __init__.py
    ├── state_manager.py    # Session state management
    ├── data_manager.py     # Data processing utilities
    └── stream_manager.py   # Stream operations
```

## Key Benefits

### 🏗️ **Maintainability**
- **Single Responsibility**: Each module has a clear, focused purpose
- **Easy Debugging**: Issues can be isolated to specific modules
- **Clean Code**: Shorter, more readable files

### 👥 **Team Collaboration**
- **Parallel Development**: Multiple developers can work on different tabs
- **Code Reviews**: Smaller, focused changes are easier to review
- **Feature Development**: New features can be added as new modules

### 📈 **Scalability**
- **Plugin Architecture**: Easy to add new tabs or utilities
- **Performance**: Better memory management and loading
- **Extensibility**: Framework for future enhancements

### 🧪 **Testing**
- **Unit Tests**: Each module can be tested independently
- **Mocking**: Easier to mock dependencies
- **Integration Testing**: Clear integration points

## Module Descriptions

### Core Modules

#### `core/app.py`
- Main application orchestration
- Interface between UI and business logic
- Session management coordination

### Tab Modules

#### `tabs/dashboard.py`
- Status overview and metrics
- Stream health monitoring
- Recent activity display

#### `tabs/streams.py`
- Stream connection management
- Detailed stream information
- Connection controls

#### `tabs/graphs.py`
- Real-time data visualization
- Multi-channel plotting
- Spectrogram analysis
- Data export functionality

#### `tabs/data.py`
- Data logging management
- Quality assessment
- Export and download features

#### `tabs/settings.py`
- Configuration management
- Performance monitoring
- Manual controls

### Utility Modules

#### `utils/state_manager.py`
- Session state initialization
- State management utilities
- Shared state access patterns

#### `utils/data_manager.py`
- Data processing functions
- Export/import utilities
- Real-time data updates

#### `utils/stream_manager.py`
- Stream connection logic
- Recording process management
- Error handling and recovery

## Migration Guide

### From Monolithic to Modular

The original `app.py` (1254 lines) has been refactored into:

- **Main App**: `app_new.py` (257 lines) - Clean orchestration
- **5 Tab Modules**: ~100-200 lines each - Focused functionality
- **3 Utility Modules**: ~50-100 lines each - Reusable components
- **Core Module**: 162 lines - Interface coordination

### Using the New Architecture

1. **Run the refactored version**:
   ```bash
   streamlit run streamlit_app/app_new.py
   ```

2. **Compare with original**:
   ```bash
   streamlit run streamlit_app/app.py
   ```

3. **Switch between versions**:
   - Rename `app_new.py` to `app.py` for production use
   - Keep original as `app_original.py` for reference

## Development Guidelines

### Adding New Tabs

1. Create new file in `tabs/` directory:
   ```python
   # tabs/my_new_tab.py
   def display_my_new_tab():
       st.header("My New Tab")
       # Implementation here
   ```

2. Import and use in `core/app.py`:
   ```python
   from ..tabs.my_new_tab import display_my_new_tab

   def render_main_interface(session_name: str, output_dir: str):
       # Add new tab to the tabs list
       tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([...])
       with tab6:
           display_my_new_tab()
   ```

### Adding New Utilities

1. Create new file in `utils/` directory:
   ```python
   # utils/my_utility.py
   def my_utility_function():
       # Implementation here
   ```

2. Export in `utils/__init__.py`:
   ```python
   from .my_utility import my_utility_function
   __all__ = ['my_utility_function', ...]
   ```

## Performance Considerations

### Memory Management
- **Lazy Loading**: Modules are imported only when needed
- **Session State**: Centralized state management prevents duplication
- **Caching**: Smart caching reduces redundant computations

### UI Responsiveness
- **Modular Updates**: Only changed components re-render
- **Background Processing**: Non-blocking data updates
- **Rate Limiting**: Configurable update frequencies

## Best Practices

### Code Organization
- **Single Responsibility**: Each module has one clear purpose
- **Dependency Injection**: Clear interfaces between modules
- **Error Handling**: Comprehensive error handling at module boundaries

### Testing Strategy
- **Unit Tests**: Test each module independently
- **Integration Tests**: Test module interactions
- **End-to-End Tests**: Test complete user workflows

### Documentation
- **Docstrings**: Every function and module documented
- **Type Hints**: Clear parameter and return types
- **Examples**: Usage examples in documentation

## Future Enhancements

### Potential Extensions
- **Plugin System**: Dynamic tab loading
- **Configuration Files**: External configuration management
- **Database Integration**: Persistent settings storage
- **User Management**: Multi-user support
- **API Endpoints**: REST API for external integration

### Monitoring & Analytics
- **Usage Tracking**: Track feature usage
- **Performance Monitoring**: Real-time performance metrics
- **Error Reporting**: Centralized error logging

## Troubleshooting

### Common Issues

1. **Import Errors**:
   ```bash
   # Check module structure
   ls -la streamlit_app/tabs/
   ls -la streamlit_app/utils/
   ```

2. **Session State Issues**:
   ```python
   # Ensure proper initialization
   from .utils.state_manager import initialize_session_state
   initialize_session_state(st)
   ```

3. **Missing Dependencies**:
   ```bash
   # Check all imports are available
   grep -r "from .." streamlit_app/
   ```

### Debug Mode
Enable debug mode by setting environment variable:
```bash
export DEBUG_MODE=1
```

This provides detailed logging and error information.

---

**Recommendation**: Use `app_new.py` for all new development. The modular architecture provides a solid foundation for future enhancements and team collaboration.
