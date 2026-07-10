# Contributing to Obsidian Pilot

Thank you for your interest in contributing to Obsidian Pilot!

## How to Contribute

### Reporting Bugs

If you find a bug, please open an issue on GitHub with:
- A clear title and description
- Steps to reproduce the issue
- Expected vs actual behavior
- Your environment (OS, Python version)

### Suggesting Features

Feature requests are welcome! Please include:
- A clear description of the feature
- Why it would be useful
- Any examples or mockups

### Submitting Code

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/my-feature`)
3. Make your changes
4. Add or update tests
5. Run the test suite (`python3 tests/test_all.py`)
6. Commit your changes (`git commit -am 'Add new feature'`)
7. Push to the branch (`git push origin feature/my-feature`)
8. Open a Pull Request

### Code Style

- Follow PEP 8 guidelines
- Use type hints where appropriate
- Write docstrings for all functions
- Keep functions small and focused
- Maximum line length: 100 characters

## Development Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/obsidian-pilot.git
cd obsidian-pilot

# Create a virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -e .

# Run tests
python3 tests/test_all.py
```

## License

By contributing to Obsidian Pilot, you agree that your contributions will be licensed under the MIT License.
