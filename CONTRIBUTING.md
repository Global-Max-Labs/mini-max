# Contributing to MiniMax 🤖

Thank you for your interest in contributing to MiniMax! This guide will help you get started with contributing to our open-source research and engineering assistant.

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Making Changes](#making-changes)
- [Testing](#testing)
- [Submitting Changes](#submitting-changes)
- [Project Structure](#project-structure)
- [Coding Standards](#coding-standards)
- [Issue Guidelines](#issue-guidelines)
- [Pull Request Process](#pull-request-process)

## Code of Conduct

By participating in this project, you agree to abide by our code of conduct. Please be respectful, inclusive, and constructive in all interactions.

## Getting Started

### Prerequisites

Before contributing, ensure you have:

- **Python** 3.11.10 or higher
- **UV** 0.7.13 or higher
- **Git** for version control
- Basic familiarity with FastAPI, MQTT, and machine learning concepts

### Fork and Clone

1. Fork the repository on GitHub
2. Clone your fork locally:
   ```bash
   git clone https://github.com/your-username/mini-max.git
   cd mini-max
   ```

## Development Setup

### 1. Install Dependencies

Install the project dependencies for your platform:

```bash
# For macOS
uv pip install ".[macos]"

# For Jetson Nano
uv pip install ".[jetson]"

# For Windows (coming soon)
uv pip install ".[windows]"
```

### 2. Environment Configuration

Create a `.env` file for optional online mode capabilities:

```bash
touch .env
echo "OPENAI_API_KEY=your_openai_api_key_here" >> .env
```

### 3. Verify Installation

Test that everything is working:

```bash
# Test CLI
minimax start

# Or run without installing CLI
python minimax/cli.py start
```

## Making Changes

### Branch Naming

Create descriptive branch names:

- `feature/audio-processing-improvement`
- `bugfix/mqtt-connection-issue`
- `docs/api-documentation-update`
- `refactor/sensor-data-collection`

### Development Workflow

1. Create a new branch:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Make your changes following our [coding standards](#coding-standards)

3. Test your changes locally

4. Commit with clear, descriptive messages:
   ```bash
   git commit -m "Add voice activity detection to audio processing

   - Implement WebRTC VAD for better silence detection
   - Reduce false positives in voice recognition
   - Add configurable sensitivity parameters"
   ```

## Testing

### Running Tests

Execute the test suite to ensure your changes don't break existing functionality:

```bash
uv run pytest tests
```

### Test Coverage

- Write tests for new features
- Ensure existing tests pass
- Aim for comprehensive coverage of critical paths

### Testing Areas

When contributing, consider testing:

- **Core Services** - MQTT, audio processing, data collection
- **API Endpoints** - FastAPI routes and responses
- **Edge Cases** - Offline mode, error handling, edge device compatibility
- **Integration** - End-to-end workflows

## Submitting Changes

### Before Submitting

1. **Format your code** using Black:
   ```bash
   black .
   ```

2. **Run tests** to ensure everything works:
   ```bash
   uv run pytest tests
   ```

3. **Update documentation** if you've changed APIs or added features

4. **Check your commit messages** are clear and descriptive

### Pull Request Process

1. Push your branch to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```

2. Create a Pull Request on GitHub with:
   - **Clear title** describing the change
   - **Detailed description** of what you've implemented
   - **Testing notes** explaining how you've tested the changes
   - **Screenshots/demos** for UI changes or new features

3. **Link related issues** using keywords like "Fixes #123" or "Addresses #456"

## Project Structure

Understanding the codebase structure will help you contribute effectively:

```
mini-max/
├── minimax/           # Core MiniMax modules
│   ├── app/          # FastAPI application
│   ├── services/     # Core service modules
│   ├── config/       # Configuration files
│   └── cli.py        # Command-line interface
├── tests/            # Test suite
├── README.md         # Project documentation
├── pyproject.toml    # Project configuration
└── CONTRIBUTING.md   # This file!
```

### Key Components

- **FastAPI App** (`minimax/app/`) - REST API endpoints
- **Services** (`minimax/services/`) - Core functionality modules
- **CLI** (`minimax/cli.py`) - Command-line interface
- **MQTT Integration** - Sensor communication and device control
- **Audio Processing** - Voice interaction capabilities
- **Vector Database** - LanceDB integration for data storage

## Coding Standards

### Python Style

- Follow **PEP 8** guidelines
- Use **Black** for code formatting (run `black .`)
- Use **type hints** where appropriate
- Write **docstrings** for public functions and classes

### Code Quality

- **Clear variable names** - Use descriptive, self-documenting names
- **Small functions** - Keep functions focused and concise
- **Error handling** - Handle edge cases and provide meaningful error messages
- **Comments** - Explain complex logic and design decisions

### Example

```python
def process_audio_chunk(audio_data: bytes, sample_rate: int = 16000) -> Optional[str]:
    """
    Process an audio chunk for voice activity detection.
    
    Args:
        audio_data: Raw audio bytes
        sample_rate: Audio sample rate in Hz
        
    Returns:
        Transcribed text if voice activity detected, None otherwise
    """
    try:
        # Implementation here
        pass
    except AudioProcessingError as e:
        logger.error(f"Audio processing failed: {e}")
        return None
```

## Issue Guidelines

### Reporting Bugs

When reporting bugs, include:

- **Clear description** of the issue
- **Steps to reproduce** the problem
- **Expected vs actual behavior**
- **Environment details** (OS, Python version, hardware)
- **Error messages** and stack traces
- **Minimal example** that reproduces the issue

### Feature Requests

For feature requests, provide:

- **Use case** - Why is this feature needed?
- **Proposed solution** - How should it work?
- **Alternatives considered** - What other approaches were considered?
- **Implementation notes** - Any technical considerations

### Labels

Use appropriate labels:

- `bug` - Something isn't working
- `enhancement` - New feature or improvement
- `documentation` - Documentation updates
- `good first issue` - Good for newcomers
- `help wanted` - Extra attention needed

## Development Focus Areas

We're particularly interested in contributions to:

- **🔌 Offline Mode** - Improving functionality without internet
- **📊 Data Analysis Tools** - EDA and visualization capabilities
- **🤖 Edge Inference** - Model optimization for edge devices
- **🎤 Audio Processing** - Voice interaction improvements
- **📡 MQTT Integration** - Sensor and device communication
- **🗄️ Database Operations** - LanceDB optimization
- **⚡ API Performance** - FastAPI endpoint optimization

## Questions?

- **Open an issue** for technical questions
- **Start a discussion** for general questions or ideas
- **Check existing issues** before creating new ones

## Recognition

Contributors will be recognized in:

- Project README
- Release notes for significant contributions
- GitHub contributor graphs

---

Thank you for contributing to MiniMax! Your efforts help make this research and engineering platform better for everyone. 🚀

**Happy coding!** 🤖✨ 