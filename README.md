# ThreatPathMapper: Attack Path Visualization & Analysis

AI-powered cybersecurity framework that automatically processes threat intelligence reports and generates structured attack paths mapped to the MITRE ATT&CK framework.

## Key Features

- **Automated Attack Path Generation**: Converts threat intelligence reports into sequential attack chains
- **MITRE ATT&CK Mapping**: Automatically identifies and maps techniques with context snippets
- **Context-Aware Analysis**: Shows which specific text snippets matched each technique
- **Multi-format Visualization**: Kill chain structure, attack narratives, tabular summaries
- **Confidence Scoring**: Provides probability scores for each technique identification

## Quick Start

### Installation

1. **Clone repository:**
   ```bash
   git clone <repository-url>
   cd ThreatPathMapper
   ```

2. **Using Docker (Recommended):**
   ```bash
   docker-compose build
   docker-compose up -d
   ```

3. **Using Local Installation:**
   ```bash
   pip install -r requirements.txt
   python -m spacy download en_core_web_lg
   ```

### Usage

1. **Place CTI reports in `data/campaign/input/`**

2. **Run analysis:**
   ```bash
   python3 main.py
   ```

3. **Generate enhanced visualization:**
   ```bash
   python3 generate_tabular_data.py "data/campaign/decoding_result/your_campaign.json"
   ```

## Enhanced Attack Chain Analysis

The system generates multiple visualization formats:

### 1. Kill Chain Structure
Organizes techniques by MITRE ATT&CK tactic phases with confidence scoring and context mapping.

### 2. Context Mapping
**NEW**: Shows specific text snippets from the original report that matched each technique:
- `'registered domains' (sentence 0)` → T1583.001 - Domains
- `'PowerShell commands' (sentence 5)` → T1059.001 - PowerShell

### 3. Attack Flow Formats
- **Executive Summary**: Simple tactic progression
- **Technical Analysis**: Detailed implementation methods and tools
- **Attack Narrative**: Story-based attack reconstruction

### Export Options
```bash
# Export to CSV and JSON
python3 generate_tabular_data.py "campaign.json" --save-csv --save-json --output-dir reports/
```

## Architecture

```
CTI Reports → NLP Processing → Graph Alignment → Attack Path Generation → Multi-format Visualization
```

**Technology Stack:**
- NLP: SpaCy, TensorFlow Hub embeddings
- Graph Processing: NetworkX 
- Visualization: Custom Python formatting

## Project Structure

```
ThreatPathMapper/
├── main.py                    # Main analysis engine
├── generate_tabular_data.py   # Enhanced visualization system
├── classes/                   # Core analysis components
├── data/campaign/
│   ├── input/                 # Your CTI reports (.txt, .html)
│   └── decoding_result/       # Generated attack paths (.json)
└── requirements.txt
```

## Common Commands

```bash
# Full analysis from scratch
python3 main.py --campaign_from_0=True

# Generate visualization with context mapping
python3 generate_tabular_data.py "data/campaign/decoding_result/campaign.json"

# Batch process multiple campaigns
for file in data/campaign/decoding_result/*.json; do
    python3 generate_tabular_data.py "$file" --save-csv
done
```

## Troubleshooting

**Memory Issues:**
```bash
# Use Docker with more memory
docker-compose run --rm -m 8g threatpathmapper python3 main.py
```

**Missing Dependencies:**
```bash
pip install tabulate spacy tensorflow-hub
python -m spacy download en_core_web_lg
```

## Based on RAF-AG Research

This project builds upon the foundational [RAF-AG research by CyberLab](https://github.com/cyb3rlab/RAF-AG) with enhancements for operational threat intelligence analysis.

---

**Important**: This framework is designed for **defensive cybersecurity research and threat analysis purposes**.