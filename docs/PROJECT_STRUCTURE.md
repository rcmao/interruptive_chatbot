# Project Structure Documentation

## Directory Structure

```
interruptive_chatbot/
├── main.py                    # Main entry point
├── src/                       # Source code
│   ├── core/                  # Core modules
│   │   ├── main.py           # Main bot logic
│   │   └── intelligent_detector.py  # Intelligent detector
│   ├── detectors/             # Detector modules
│   │   ├── scenario_detector.py     # Scenario-specific detection
│   │   ├── realtime_detector.py     # Real-time detection
│   │   └── optimized_monitor.py     # Optimized monitoring
│   ├── interventions/         # Intervention modules
│   │   ├── scenario_intervention.py # Scenario intervention
│   │   └── intervention_generator.py # Intervention generator
│   ├── models/               # Model modules
│   │   ├── thomas_model.py   # Thomas conflict model
│   │   └── prompt_templates.py # Prompt templates
│   └── utils/                # Utility modules
│       ├── network_test.py   # Network testing
│       ├── discord_check.py  # Discord permission check
│       └── data_collector.py # Data collection
├── tests/                    # Test files
│   ├── unit/                 # Unit tests
│   ├── integration/          # Integration tests
│   └── scenarios/            # Scenario tests
├── config/                   # Configuration files
│   ├── requirements.txt      # Dependencies
│   ├── pytest.ini          # Test configuration
│   └── .env.template        # Environment variables template
├── docs/                     # Documentation
│   ├── README.md            # Project documentation
│   └── system_design.tex    # System design document
├── scripts/                  # Scripts
│   ├── start.sh             # Start script
│   └── run_tests.sh         # Test script
├── data/                     # Data files
├── logs/                     # Log files
└── backup/                   # Backup files
```

## Quick Start

1. **Install Dependencies**
   ```bash
   pip install -r config/requirements.txt
   ```

2. **Configure Environment Variables**
   ```bash
   cp config/.env.template .env
   # Edit .env file with your Discord Token and OpenAI API Key
   ```

3. **Start Bot**
   ```bash
   python main.py
   # Or use script
   ./scripts/start.sh
   ```

4. **Run Tests**
   ```bash
   ./scripts/run_tests.sh
   ```

## Testing

- **Unit Tests**: `python -m pytest tests/unit/`
- **Integration Tests**: `python -m pytest tests/integration/`
- **Scenario Tests**: `python -m pytest tests/scenarios/`

## System Features

- **Intelligent Context Awareness**: Based on conversation history and emotion trajectory
- **Subtle Signal Detection**: Captures implicit emotions like "??", "..."
- **Dynamic Threshold System**: Automatically adjusts sensitivity based on conversation state
- **Real-time Performance**: <300ms response time
- **Explainability**: Complete decision explanation and evidence chain
