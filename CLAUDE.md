# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

FinGenius is the world's first A-share AI financial multi-agent application using a Research-Battle dual-environment architecture. It employs 6 specialized agents (sentiment, hot money, risk control, technical analysis, chip analysis, big deal analysis) that collaborate through research and debate phases to generate comprehensive stock analysis reports.

## Core Architecture

### Dual Environment System
- **Research Environment**: Sequential analysis by 6 specialized agents with 3-second intervals
- **Battle Environment**: Multi-round structured debate with voting mechanism
- **State Management**: Complete context transfer between environments

### Agent Hierarchy
```
BaseAgent (abstract)
├── ReActAgent (abstract)
│   └── ToolCallAgent (abstract)
│       └── MCPAgent (concrete)
│           ├── SentimentAgent (舆情)
│           ├── RiskControlAgent (风控)
│           ├── HotMoneyAgent (游资)
│           ├── TechnicalAnalysisAgent (技术分析)
│           ├── ChipAnalysisAgent (筹码分析)
│           ├── BigDealAnalysisAgent (大单异动)
│           └── ReportAgent (报告生成)
```

## Development Commands

### Environment Setup
```bash
# Using uv (recommended) - 10-50x faster than pip
uv venv --python 3.12
source .venv/bin/activate  # Windows: .venv\Scripts\activate
uv pip install -r requirements.txt

# Using conda
conda create -n fingenius python=3.12
conda activate fingenius
pip install -r requirements.txt
```

### Configuration
```bash
# Copy config template
cp config/config.example.toml config/config.toml
# Edit config.toml with your LLM API settings
```

### Running Analysis
```bash
# Basic stock analysis
python main.py 000001

# With custom parameters
python main.py 000001 --debate-rounds 3 --max-steps 5

# JSON output with file save
python main.py 000001 --format json --output report.json

# Enable TTS voice announcement
python main.py 000001 --tts
```

### Testing Individual Components
```bash
# Test specific agent
python -c "from src.agent.sentiment import SentimentAgent; import asyncio; asyncio.run(SentimentAgent.create().run('000001'))"

# Test environment
python -c "from src.environment.research import ResearchEnvironment; import asyncio; asyncio.run(ResearchEnvironment.create().run('000001'))"
```

## Key Technical Patterns

### Agent Creation Pattern
All agents follow the async factory pattern:
```python
agent = await SpecificAgent.create(max_steps=3)
```

### Tool Integration
- MCP (Model Context Protocol) for external tool integration
- Financial APIs: efinance, akshare for real-time data
- Multi-engine search with fallback (Bing recommended for China)

### State Management
- Agents maintain separate memories in Research phase
- Complete research results passed to all agents in Battle phase
- Cumulative debate context with all previous arguments

### Report Generation
- HTML reports with charts and debate logs saved to `report/`
- JSON data saved for debate history and vote results
- TTS audio files saved to `results/` when enabled

## Configuration Details

### LLM Settings (config/config.toml)
- Supports OpenAI, Azure OpenAI, and Ollama
- Recommended: Claude 3.7 Sonnet for best results
- Temperature: 0.0 for consistent analysis
- Max tokens: 8192 for comprehensive responses

### Search Configuration
- Default: Bing (stable in China)
- Alternatives: Baidu, Google, DuckDuckGo
- Set in config.toml: `engine = "Bing"`

## Common Development Tasks

### Adding New Agent
1. Create agent class in `src/agent/` inheriting from `MCPAgent`
2. Add system prompt in `src/prompt/`
3. Register in `ResearchEnvironment.initialize()`
4. Add analysis mapping key
5. Update battle environment registration

### Adding New Tool
1. Create tool class in `src/tool/` inheriting from `BaseTool`
2. Add to agent's available tools in `ToolCollection`
3. Follow existing patterns for financial data retrieval

### Debugging
- Enable verbose logging: `export LOG_LEVEL=DEBUG`
- Check logs in `logs/` directory
- Use `--format json` for structured output

## Important Notes

- **API Keys**: Never commit API keys to repository
- **Rate Limiting**: Agents run with 3-second intervals by default
- **Memory Management**: Clean up environments after use to prevent warnings
- **Network Issues**: Use Bing/Baidu for China network compatibility
- **File Paths**: Always use absolute paths for file operations
- **Error Handling**: Agents have built-in retry mechanisms with tenacity