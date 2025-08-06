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
   # Build the Docker image
   docker-compose build
   
   # Start the container in detached mode
   docker-compose up -d
   
   # Access the container to run commands
   docker-compose exec threatpathmapper /bin/bash
   
   # Inside the container, run analysis
   python3 main.py
   
   # Generate enhanced visualization
   python3 generate_tabular_data.py "data/campaign/decoding_result/your_campaign.json"
   
   # Stop the container when done
   docker-compose down
   ```

3. **Using Local Installation:**
   ```bash
   pip install -r requirements.txt
   python -m spacy download en_core_web_lg
   ```

### Docker Usage (Detailed)

1. **Prepare your CTI reports:**
   ```bash
   # Place your threat intelligence reports in the input directory
   # Supports .txt, .html, .pdf formats
   cp your_threat_report.txt data/campaign/input/
   ```

2. **Run complete analysis with Docker:**
   ```bash
   # Method 1: Interactive container access
   docker-compose build && docker-compose up -d
   docker-compose exec threatpathmapper /bin/bash
   
   # Inside container:
   python3 main.py --campaign_from_0=True
   python3 generate_tabular_data.py "data/campaign/decoding_result/your_report.json"
   exit
   
   # Method 2: Direct command execution
   docker-compose run --rm threatpathmapper python3 main.py --campaign_from_0=True
   docker-compose run --rm threatpathmapper python3 generate_tabular_data.py "data/campaign/decoding_result/your_report.json"
   
   # Method 3: One-liner for quick analysis
   docker-compose run --rm threatpathmapper /bin/bash -c "python3 main.py --campaign_from_0=True && python3 generate_tabular_data.py data/campaign/decoding_result/*.json"
   ```

3. **Memory allocation for large reports:**
   ```bash
   # Allocate more memory for large CTI reports
   docker-compose run --rm -m 8g threatpathmapper python3 main.py
   ```

4. **Access results:**
   ```bash
   # Results are saved in the mounted volumes
   # View generated attack chains
   ls -la data/campaign/decoding_result/
   
   # Export results with Docker
   docker-compose run --rm threatpathmapper python3 generate_tabular_data.py \
     "data/campaign/decoding_result/your_report.json" --save-csv --output-dir reports/
   ```

### Local Usage

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

### Docker Issues

**Container not starting:**
```bash
# Check if Docker is running
docker version

# Rebuild the image
docker-compose build --no-cache

# Check logs
docker-compose logs threatpathmapper
```

**Memory Issues:**
```bash
# Allocate more memory to Docker container
docker-compose run --rm -m 8g threatpathmapper python3 main.py

# Or modify docker-compose.yml to add memory limits:
# deploy:
#   resources:
#     limits:
#       memory: 8G
```

**Permission Issues:**
```bash
# Fix file permissions
sudo chown -R $USER:$USER data/
chmod -R 755 data/
```

**Container Access Issues:**
```bash
# List running containers
docker ps

# Force stop and restart
docker-compose down --remove-orphans
docker-compose up -d

# Access container with different shell
docker-compose exec threatpathmapper /bin/sh
```

### Local Installation Issues

**Missing Dependencies:**
```bash
pip install tabulate spacy tensorflow-hub
python -m spacy download en_core_web_lg
```

**SpaCy Model Issues:**
```bash
# Download required models
python -m spacy download en_core_web_lg
python -m spacy download en_core_web_trf
python -m coreferee install en
```

## Based on RAF-AG Research

This project builds upon the foundational [RAF-AG research by CyberLab](https://github.com/cyb3rlab/RAF-AG) with enhancements for operational threat intelligence analysis.

---

**Important**: This framework is designed for **defensive cybersecurity research and threat analysis purposes**.