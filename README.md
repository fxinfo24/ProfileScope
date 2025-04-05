# ProfileScope

A comprehensive social media profile analysis tool that provides deep insights into social media profiles through advanced data analysis, behavioral patterns, and authenticity verification.

## Features

- Multi-platform social media data collection (Twitter, Facebook)
- Advanced content analysis using NLP
- Personality trait inference
- Writing style analysis
- Timeline visualization
- Authenticity verification
- Predictive analytics
- Both web and desktop interfaces

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/profilescope.git
cd profilescope
```

2. Create a virtual environment and activate it:
```bash
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
```

2.1. Create a virtual environment with specific Python version and activate it:
```bash
python3.12 -m venv venv --prompt="ProfileScope"
# For bash/zsh shells
source venv/bin/activate

# Or using . shortcut
. venv/bin/activate
```


3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure your settings:
- Copy `config.json` to `config.local.json`
- Add your API credentials and customize settings

## Usage

### Command Line Interface

Analyze a profile:
```bash
python run.py --platform twitter --profile username
```

Options:
- `--platform`: Social media platform (twitter/facebook)
- `--profile`: Username or profile ID to analyze
- `--config`: Path to custom config file
- `--output`: Custom output file path
- `--verbose`: Enable detailed logging

### Desktop Application

Launch the desktop GUI:
```bash
python -m app.desktop.app
```

### Web Interface

Start the web server:
```bash
python -m app.web.app
```

Access the web interface at `http://localhost:5000`

## Development

### Project Structure

- `app/core/`: Core analysis engine
- `app/desktop/`: Desktop GUI application
- `app/web/`: Web application
- `app/utils/`: Utility functions
- `tests/`: Test suites
- `data/`: Data storage
- `docs/`: Documentation

### Running Tests

```bash
pytest tests/
```

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Thanks to all contributors
- Built with Python and modern data analysis libraries
- Powered by machine learning and NLP technologies

## Support

For support, please:
1. Check the documentation in the `docs/` directory
2. Open an issue on GitHub
3. Contact the development team
