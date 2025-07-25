#!/usr/bin/env python3
"""
ThreatPathMapper - Enhanced Attack Chain Visualization & Analysis
Script to generate tabular attack chain data from RAF-AG results.
Converts JSON attack path data into a structured tabular format similar to the MITRE ATT&CK kill chain view.
"""

import json
import csv
import argparse
import os
from tabulate import tabulate
from typing import Dict, List, Any, Optional, Tuple

# MITRE ATT&CK Tactic mapping
MITRE_TACTICS = {
    "TA0042": "Resource Development",
    "TA0001": "Initial Access",
    "TA0002": "Execution", 
    "TA0003": "Persistence",
    "TA0004": "Privilege Escalation",
    "TA0005": "Defense Evasion",
    "TA0006": "Credential Access",
    "TA0007": "Discovery",
    "TA0008": "Lateral Movement",
    "TA0009": "Collection",
    "TA0011": "Command and Control",
    "TA0010": "Exfiltration",
    "TA0040": "Impact"
}

# Tactic execution order for attack chain flow
TACTIC_ORDER = [
    "TA0042", "TA0001", "TA0002", "TA0003", "TA0004", 
    "TA0005", "TA0006", "TA0007", "TA0008", "TA0009", 
    "TA0011", "TA0010", "TA0040"
]

# Comprehensive Technique to Tactic mapping
TECHNIQUE_TO_TACTIC = {
    # Resource Development
    "T1583": "TA0042", "T1584": "TA0042", "T1585": "TA0042", "T1586": "TA0042",
    "T1587": "TA0042", "T1588": "TA0042", "T1608": "TA0042",
    
    # Initial Access
    "T1566": "TA0001", "T1190": "TA0001", "T1199": "TA0001", "T1091": "TA0001",
    "T1195": "TA0001", "T1200": "TA0001", "T1078": "TA0001", "T1133": "TA0001",
    "T1189": "TA0001",
    
    # Execution
    "T1059": "TA0002", "T1203": "TA0002", "T1127": "TA0002", "T1204": "TA0002",
    "T1053": "TA0002", "T1129": "TA0002", "T1609": "TA0002", "T1610": "TA0002",
    "T1047": "TA0002", "T1106": "TA0002", "T1559": "TA0002",
    
    # Persistence
    "T1547": "TA0003", "T1136": "TA0003", "T1543": "TA0003", "T1574": "TA0003",
    "T1546": "TA0003", "T1505": "TA0003", "T1137": "TA0003", "T1098": "TA0003",
    "T1176": "TA0003", "T1554": "TA0003", "T1133": "TA0003",
    
    # Privilege Escalation
    "T1055": "TA0004", "T1548": "TA0004", "T1134": "TA0004", "T1484": "TA0004",
    "T1068": "TA0004", "T1611": "TA0004", "T1574": "TA0004", "T1053": "TA0004",
    "T1543": "TA0004", "T1546": "TA0004", "T1547": "TA0004",
    
    # Defense Evasion
    "T1140": "TA0005", "T1070": "TA0005", "T1027": "TA0005", "T1562": "TA0005",
    "T1055": "TA0005", "T1036": "TA0005", "T1218": "TA0005", "T1620": "TA0005",
    "T1134": "TA0005", "T1574": "TA0005", "T1112": "TA0005", "T1127": "TA0005",
    
    # Credential Access
    "T1003": "TA0006", "T1110": "TA0006", "T1555": "TA0006", "T1212": "TA0006",
    "T1552": "TA0006", "T1040": "TA0006", "T1556": "TA0006", "T1558": "TA0006",
    "T1111": "TA0006", "T1621": "TA0006",
    
    # Discovery
    "T1018": "TA0007", "T1082": "TA0007", "T1083": "TA0007", "T1087": "TA0007",
    "T1057": "TA0007", "T1135": "TA0007", "T1046": "TA0007", "T1016": "TA0007",
    "T1033": "TA0007", "T1124": "TA0007", "T1007": "TA0007", "T1012": "TA0007",
    "T1049": "TA0007", "T1069": "TA0007", "T1201": "TA0007",
    
    # Lateral Movement
    "T1021": "TA0008", "T1210": "TA0008", "T1534": "TA0008", "T1570": "TA0008",
    "T1550": "TA0008", "T1563": "TA0008", "T1080": "TA0008", "T1072": "TA0008",
    "T1091": "TA0008", "T1051": "TA0008",
    
    # Collection
    "T1005": "TA0009", "T1074": "TA0009", "T1039": "TA0009", "T1025": "TA0009",
    "T1113": "TA0009", "T1114": "TA0009", "T1123": "TA0009", "T1560": "TA0009",
    "T1119": "TA0009", "T1115": "TA0009", "T1125": "TA0009",
    
    # Command and Control
    "T1573": "TA0011", "T1008": "TA0011", "T1071": "TA0011", "T1090": "TA0011",
    "T1568": "TA0011", "T1105": "TA0011", "T1102": "TA0011", "T1095": "TA0011",
    "T1132": "TA0011", "T1001": "TA0011", "T1104": "TA0011",
    
    # Exfiltration
    "T1029": "TA0010", "T1041": "TA0010", "T1011": "TA0010", "T1052": "TA0010",
    "T1567": "TA0010", "T1020": "TA0010", "T1030": "TA0010", "T1048": "TA0010",
    "T1022": "TA0010", "T1537": "TA0010",
    
    # Impact
    "T1485": "TA0040", "T1486": "TA0040", "T1491": "TA0040", "T1565": "TA0040",
    "T1499": "TA0040", "T1498": "TA0040", "T1529": "TA0040", "T1561": "TA0040",
    "T1490": "TA0040", "T1657": "TA0040",
}

# MITRE ATT&CK technique descriptions and implementation methods
TECHNIQUE_DETAILS = {
    "T1583.001": {
        "description": "Adversaries acquire domains for malicious purposes including phishing, drive-by compromise, and command and control.",
        "implementation": ["Domain purchasing", "Typosquatting", "IDN homograph attacks", "Expired domain reuse"],
        "tools": ["Domain registrars", "WHOIS privacy services", "DNS management tools"]
    },
    "T1566.001": {
        "description": "Adversaries send spearphishing emails with malicious attachments to gain initial access.",
        "implementation": ["Malicious documents", "Macro-enabled files", "Archive attachments", "PDF exploits"],
        "tools": ["Email clients", "Document generators", "Exploit kits", "Social engineering"]
    },
    "T1003": {
        "description": "Adversaries attempt to dump credentials from operating system credential storage.",
        "implementation": ["LSASS dumping", "Registry extraction", "Memory scraping", "Hash extraction"],
        "tools": ["Mimikatz", "ProcDump", "Impacket", "LaZagne", "Windows Credential Editor"]
    },
    "T1059": {
        "description": "Adversaries abuse command and script interpreters to execute commands and scripts.",
        "implementation": ["PowerShell scripts", "Command line execution", "Batch files", "Shell commands"],
        "tools": ["PowerShell", "cmd.exe", "bash", "Python", "JavaScript"]
    },
    "T1055": {
        "description": "Adversaries inject code into processes to evade process-based defenses and elevate privileges.",
        "implementation": ["DLL injection", "Process hollowing", "Thread execution hijacking", "Portable executable injection"],
        "tools": ["Reflective DLL loading", "Process injection frameworks", "Manual mapping tools"]
    }
}

# Common tools associated with MITRE ATT&CK techniques
COMMON_TOOLS = {
    "credential_access": ["Mimikatz", "LaZagne", "Impacket", "BloodHound", "Rubeus"],
    "execution": ["PowerShell", "cmd.exe", "Cobalt Strike", "Metasploit", "Empire"],
    "persistence": ["Scheduled tasks", "Registry modifications", "Service creation", "WMI subscriptions"],
    "lateral_movement": ["PsExec", "WMI", "PowerShell remoting", "RDP", "SSH"],
    "defense_evasion": ["Process injection", "AMSI bypass", "Obfuscation", "Living off the land binaries"]
}

class AttackChainTableGenerator:
    def __init__(self):
        self.attack_chain_data = []
        self.attack_paths = []
        
    def load_raf_data(self, json_file_path: str) -> Dict[str, Any]:
        """Load RAF-AG JSON results file."""
        try:
            with open(json_file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading JSON file {json_file_path}: {e}")
            return {}
    
    def get_tactic_from_technique(self, technique_id: str) -> str:
        """Extract tactic from technique ID using mapping."""
        base_technique = technique_id.split('.')[0]  # Remove sub-technique part
        return TECHNIQUE_TO_TACTIC.get(base_technique, "Unknown")
    
    def get_technique_description(self, technique_id: str) -> Dict[str, Any]:
        """Get comprehensive technique description and implementation details."""
        base_technique = technique_id.split('.')[0]
        
        if technique_id in TECHNIQUE_DETAILS:
            return TECHNIQUE_DETAILS[technique_id]
        elif base_technique in TECHNIQUE_DETAILS:
            return TECHNIQUE_DETAILS[base_technique]
        else:
            # Default description based on tactic
            tactic_id = self.get_tactic_from_technique(technique_id)
            tactic_name = MITRE_TACTICS.get(tactic_id, "Unknown")
            
            return {
                "description": f"Technique related to {tactic_name} phase of the attack.",
                "implementation": ["Various methods depending on environment"],
                "tools": self._get_tools_by_tactic(tactic_id)
            }
    
    def _get_tools_by_tactic(self, tactic_id: str) -> List[str]:
        """Get common tools associated with a tactic."""
        tactic_tool_mapping = {
            "TA0006": COMMON_TOOLS["credential_access"],
            "TA0002": COMMON_TOOLS["execution"],
            "TA0003": COMMON_TOOLS["persistence"],
            "TA0008": COMMON_TOOLS["lateral_movement"],
            "TA0005": COMMON_TOOLS["defense_evasion"]
        }
        return tactic_tool_mapping.get(tactic_id, ["Various tools"])
    
    def extract_technique_details(self, technique_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract technique details and create comprehensive description."""
        details = []
        
        # Extract phrases and create meaningful details
        if 'phrases' in technique_data:
            for phrase in technique_data['phrases']:
                if 'source' in phrase and 'text' in phrase['source']:
                    details.append(phrase['source']['text'])
                if 'dest' in phrase and 'text' in phrase['dest']:
                    details.append(phrase['dest']['text'])
        
        # Create a concise detail string
        unique_details = list(set(details))[:3]  # Limit to 3 unique details
        observed_indicators = ", ".join(unique_details) if unique_details else "No specific indicators"
        
        # Get technique description
        technique_id = technique_data.get('techID', 'Unknown')
        tech_info = self.get_technique_description(technique_id)
        
        return {
            'observed_indicators': observed_indicators,
            'confidence': technique_data.get('value', 0.0),
            'description': tech_info['description'],
            'implementation_methods': tech_info['implementation'],
            'associated_tools': tech_info['tools']
        }
    
    def generate_kill_chain_structure(self, raf_data: Dict[str, Any]) -> Dict[str, List[Dict[str, Any]]]:
        """Generate kill chain structure organized by MITRE ATT&CK tactics."""
        if 'best' not in raf_data:
            return {}
            
        # Group techniques by tactic
        kill_chain = {tactic_id: [] for tactic_id in TACTIC_ORDER}
        
        # Process all techniques
        for step_key, techniques in raf_data['best'].items():
            for technique in techniques:
                technique_id = technique.get('techID', 'Unknown')
                technique_name = technique.get('tech_name', technique.get('techName', 'Unknown'))
                confidence = technique.get('value', 0.0)
                
                # Get tactic information
                tactic_id = self.get_tactic_from_technique(technique_id)
                tactic_name = MITRE_TACTICS.get(tactic_id, "Unknown Tactic")
                
                # Extract technique details
                details_info = self.extract_technique_details(technique)
                
                technique_info = {
                    'step': int(step_key),
                    'technique_id': technique_id,
                    'technique_name': technique_name,
                    'confidence': confidence,
                    'tactic_id': tactic_id,
                    'tactic_name': tactic_name,
                    'observed_indicators': details_info['observed_indicators'],
                    'description': details_info['description'],
                    'implementation_methods': details_info['implementation_methods'],
                    'associated_tools': details_info['associated_tools']
                }
                
                # Add to appropriate tactic group
                if tactic_id in kill_chain:
                    kill_chain[tactic_id].append(technique_info)
                else:
                    # Handle unknown tactics
                    if 'Unknown' not in kill_chain:
                        kill_chain['Unknown'] = []
                    kill_chain['Unknown'].append(technique_info)
        
        # Sort techniques within each tactic by confidence and step order
        for tactic_id in kill_chain:
            kill_chain[tactic_id].sort(key=lambda x: (-x['confidence'], x['step']))
        
        # Remove empty tactic groups
        kill_chain = {k: v for k, v in kill_chain.items() if v}
        
        return kill_chain
    
    def generate_attack_paths(self, kill_chain: Dict[str, List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
        """Generate logical attack paths from kill chain structure."""
        paths = []
        
        # Get tactics in order that have techniques
        active_tactics = []
        for tactic_id in TACTIC_ORDER:
            if tactic_id in kill_chain and kill_chain[tactic_id]:
                active_tactics.append(tactic_id)
        
        # Add unknown tactics at the end
        if 'Unknown' in kill_chain and kill_chain['Unknown']:
            active_tactics.append('Unknown')
        
        # Generate paths between consecutive tactics
        for i in range(len(active_tactics) - 1):
            current_tactic = active_tactics[i]
            next_tactic = active_tactics[i + 1]
            
            current_techniques = kill_chain[current_tactic]
            next_techniques = kill_chain[next_tactic]
            
            # Create primary path (highest confidence techniques)
            if current_techniques and next_techniques:
                primary_current = current_techniques[0]
                primary_next = next_techniques[0]
                
                path = {
                    'from_tactic': MITRE_TACTICS.get(current_tactic, current_tactic),
                    'from_technique': f"{primary_current['technique_id']} - {primary_current['technique_name']}",
                    'to_tactic': MITRE_TACTICS.get(next_tactic, next_tactic),
                    'to_technique': f"{primary_next['technique_id']} - {primary_next['technique_name']}",
                    'confidence_score': (primary_current['confidence'] + primary_next['confidence']) / 2,
                    'path_type': 'Primary'
                }
                paths.append(path)
                
                # Add alternative paths if multiple techniques exist
                for alt_current in current_techniques[1:2]:  # Limit to 1 alternative
                    for alt_next in next_techniques[1:2]:
                        alt_path = {
                            'from_tactic': MITRE_TACTICS.get(current_tactic, current_tactic),
                            'from_technique': f"{alt_current['technique_id']} - {alt_current['technique_name']}",
                            'to_tactic': MITRE_TACTICS.get(next_tactic, next_tactic),
                            'to_technique': f"{alt_next['technique_id']} - {alt_next['technique_name']}",
                            'confidence_score': (alt_current['confidence'] + alt_next['confidence']) / 2,
                            'path_type': 'Alternative'
                        }
                        paths.append(alt_path)
        
        return paths
    
    def generate_tabular_data(self, raf_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate enhanced tabular data from RAF-AG results."""
        tabular_data = []
        
        # Process the best path results
        if 'best' in raf_data:
            for step_key, techniques in raf_data['best'].items():
                for technique in techniques:
                    technique_id = technique.get('techID', 'Unknown')
                    technique_name = technique.get('tech_name', technique.get('techName', 'Unknown'))
                    
                    # Get tactic information
                    tactic_id = self.get_tactic_from_technique(technique_id)
                    tactic_name = MITRE_TACTICS.get(tactic_id, "Unknown Tactic")
                    
                    # Extract comprehensive details
                    details_info = self.extract_technique_details(technique)
                    
                    # Create enhanced table row
                    row = {
                        'Stage': f"Step {step_key}",
                        'Tactic (MITRE)': f"{tactic_id} - {tactic_name}",
                        'Technique': f"{technique_id} - {technique_name}",
                        'Description': details_info['description'],
                        'Implementation Methods': "; ".join(details_info['implementation_methods']),
                        'Associated Tools': "; ".join(details_info['associated_tools']),
                        'Observed Indicators': details_info['observed_indicators'],
                        'Confidence': f"{details_info['confidence']:.3f}"
                    }
                    tabular_data.append(row)
        
        # Sort by step order
        tabular_data.sort(key=lambda x: int(x['Stage'].split()[-1]))
        
        # Generate kill chain structure and attack paths
        self.kill_chain = self.generate_kill_chain_structure(raf_data)
        self.attack_paths = self.generate_attack_paths(self.kill_chain)
        
        return tabular_data
    
    def print_kill_chain_structure(self):
        """Print kill chain structure organized by MITRE ATT&CK tactics."""
        if not hasattr(self, 'kill_chain') or not self.kill_chain:
            return
            
        print("\n### Kill Chain Structure (Organized by MITRE ATT&CK Tactics)")
        print("="*80)
        
        for tactic_id in TACTIC_ORDER:
            if tactic_id in self.kill_chain and self.kill_chain[tactic_id]:
                tactic_name = MITRE_TACTICS.get(tactic_id, tactic_id)
                techniques = self.kill_chain[tactic_id]
                
                print(f"\n🎯 {tactic_id} - {tactic_name.upper()}")
                print("-" * 50)
                
                for i, tech in enumerate(techniques, 1):
                    confidence_bar = "█" * int(tech['confidence'] * 10) + "░" * (10 - int(tech['confidence'] * 10))
                    print(f"  {i}. {tech['technique_id']} - {tech['technique_name']}")
                    print(f"     Confidence: {confidence_bar} {tech['confidence']:.3f}")
                    print(f"     Step: {tech['step']} | Observed: {tech['observed_indicators'][:60]}...")
                    if i < len(techniques):
                        print()
        
        # Handle unknown tactics
        if 'Unknown' in self.kill_chain and self.kill_chain['Unknown']:
            print(f"\n❓ UNKNOWN TACTICS")
            print("-" * 50)
            for i, tech in enumerate(self.kill_chain['Unknown'], 1):
                confidence_bar = "█" * int(tech['confidence'] * 10) + "░" * (10 - int(tech['confidence'] * 10))
                print(f"  {i}. {tech['technique_id']} - {tech['technique_name']}")
                print(f"     Confidence: {confidence_bar} {tech['confidence']:.3f}")
                print(f"     Step: {tech['step']} | Observed: {tech['observed_indicators'][:60]}...")
                if i < len(self.kill_chain['Unknown']):
                    print()
    
    def print_simple_attack_flow(self):
        """Print simple linear attack flow."""
        if not hasattr(self, 'kill_chain') or not self.kill_chain:
            return
            
        print("\n### Simple Attack Flow")
        print("="*80)
        
        # Get active tactics in order
        active_tactics = []
        for tactic_id in TACTIC_ORDER:
            if tactic_id in self.kill_chain and self.kill_chain[tactic_id]:
                tactic_name = MITRE_TACTICS.get(tactic_id, tactic_id)
                active_tactics.append(tactic_name)
        
        # Add unknown tactics
        if 'Unknown' in self.kill_chain and self.kill_chain['Unknown']:
            active_tactics.append('Unknown Tactics')
        
        # Print linear flow
        if active_tactics:
            flow = " → ".join(active_tactics)
            print(f"\n{flow}")
            print()
    
    def print_attack_story(self):
        """Print attack story format."""
        if not hasattr(self, 'attack_paths') or not self.attack_paths:
            return
            
        print("\n### Attack Story")
        print("="*80)
        
        # Get primary paths only
        primary_paths = [p for p in self.attack_paths if p['path_type'] == 'Primary']
        
        if primary_paths:
            print("\n📖 Complete Attack Narrative:")
            print("-" * 50)
            
            # Create story from primary path
            story_steps = []
            
            # Add first step
            if primary_paths:
                first_path = primary_paths[0]
                first_technique = first_path['from_technique'].split(' - ')[0]
                first_action = self._get_technique_action(first_technique, first_path['from_tactic'])
                story_steps.append(f"1. Attackers {first_action}")
            
            # Add subsequent steps
            for i, path in enumerate(primary_paths, 2):
                technique_id = path['to_technique'].split(' - ')[0]
                action = self._get_technique_action(technique_id, path['to_tactic'])
                story_steps.append(f"{i}. {action}")
            
            for step in story_steps:
                print(step)
            print()
    
    def _get_technique_action(self, technique_id: str, tactic: str) -> str:
        """Get human-readable action description for a technique."""
        actions = {
            'T1588.001': 'develop malware for the attack',
            'T1190': 'exploit public-facing application to gain access',
            'T1059.001': 'execute PowerShell commands',
            'T1133': 'establish persistence via external remote services',
            'T1546.008': 'escalate privileges using accessibility features',
            'T1562.001': 'disable security tools and monitoring',
            'T1003': 'dump operating system credentials',
            'T1046': 'discover network services and systems',
            'T1021.006': 'move laterally via Windows Remote Management',
            'T1119': 'collect data automatically from systems',
            'T1071.001': 'communicate via web protocols for C2',
            'T1583.001': 'acquire domains for malicious purposes',
            'T1566.001': 'send spearphishing emails with attachments',
            'T1505.003': 'deploy web shells for persistence',
            'T1047': 'use Windows Management Instrumentation',
            'T1070.009': 'clear persistence mechanisms',
            'T1012': 'query registry for information',
            'T1124': 'discover system time information'
        }
        
        if technique_id in actions:
            return actions[technique_id]
        else:
            # Generate generic action based on tactic
            generic_actions = {
                'Resource Development': 'prepare attack resources',
                'Initial Access': 'gain initial access to the system',
                'Execution': 'execute malicious code',
                'Persistence': 'establish persistence mechanisms',
                'Privilege Escalation': 'escalate privileges',
                'Defense Evasion': 'evade security defenses',
                'Credential Access': 'access stored credentials',
                'Discovery': 'discover system and network information',
                'Lateral Movement': 'move laterally through the network',
                'Collection': 'collect data of interest',
                'Command and Control': 'establish command and control',
                'Exfiltration': 'exfiltrate collected data',
                'Impact': 'cause impact on systems'
            }
            return generic_actions.get(tactic, f'perform {tactic.lower()} activities')
    
    def print_tabular_summary(self):
        """Print tabular summary format."""
        if not hasattr(self, 'kill_chain') or not self.kill_chain:
            return
            
        print("\n### Attack Summary Table")
        print("="*80)
        
        # Prepare data for table
        summary_data = []
        
        for tactic_id in TACTIC_ORDER:
            if tactic_id in self.kill_chain and self.kill_chain[tactic_id]:
                tactic_name = MITRE_TACTICS.get(tactic_id, tactic_id)
                # Get highest confidence technique for each tactic
                top_technique = self.kill_chain[tactic_id][0]
                technique_id = top_technique['technique_id']
                action = self._get_technique_action(technique_id, tactic_name)
                
                summary_data.append({
                    'Phase': tactic_name,
                    'Technique': technique_id,
                    'Action': action.capitalize(),
                    'Confidence': f"{top_technique['confidence']:.3f}"
                })
        
        # Add unknown tactics
        if 'Unknown' in self.kill_chain and self.kill_chain['Unknown']:
            for tech in self.kill_chain['Unknown'][:3]:  # Limit to top 3
                summary_data.append({
                    'Phase': 'Unknown',
                    'Technique': tech['technique_id'],
                    'Action': tech['technique_name'],
                    'Confidence': f"{tech['confidence']:.3f}"
                })
        
        if summary_data:
            # Print table headers
            print(f"{'Phase':<20} {'Technique':<12} {'Action':<50} {'Confidence':<10}")
            print("-" * 92)
            
            # Print table rows
            for row in summary_data:
                action_truncated = row['Action'][:47] + "..." if len(row['Action']) > 50 else row['Action']
                print(f"{row['Phase']:<20} {row['Technique']:<12} {action_truncated:<50} {row['Confidence']:<10}")
            print()
    
    def print_attack_paths(self):
        """Print all attack path formats."""
        # Print all three simple formats
        self.print_simple_attack_flow()
        self.print_attack_story()
        self.print_tabular_summary()
        
        # Original detailed format (optional - can be commented out)
        if not hasattr(self, 'attack_paths') or not self.attack_paths:
            return
            
        print("\n### Detailed Attack Progression Paths")
        print("="*80)
        
        # Group paths by type
        primary_paths = [p for p in self.attack_paths if p['path_type'] == 'Primary']
        alternative_paths = [p for p in self.attack_paths if p['path_type'] == 'Alternative']
        
        if primary_paths:
            print("\n🔥 PRIMARY ATTACK PATH (Highest Confidence)")
            print("-" * 50)
            for i, path in enumerate(primary_paths, 1):
                confidence_bar = "█" * int(path['confidence_score'] * 10) + "░" * (10 - int(path['confidence_score'] * 10))
                print(f"{i}. {path['from_tactic']}")
                print(f"   └─ {path['from_technique']}")
                print(f"   ↓")
                print(f"   {path['to_tactic']}")
                print(f"   └─ {path['to_technique']}")
                print(f"   Confidence: {confidence_bar} {path['confidence_score']:.3f}")
                if i < len(primary_paths):
                    print()
        
        if alternative_paths:
            print("\n🔀 ALTERNATIVE PATHS")
            print("-" * 50)
            for i, path in enumerate(alternative_paths[:3], 1):  # Limit to 3 alternatives
                confidence_bar = "█" * int(path['confidence_score'] * 10) + "░" * (10 - int(path['confidence_score'] * 10))
                print(f"{i}. {path['from_tactic']} → {path['to_tactic']}")
                print(f"   {path['from_technique']} → {path['to_technique']}")
                print(f"   Confidence: {confidence_bar} {path['confidence_score']:.3f}")
                if i < min(len(alternative_paths), 3):
                    print()
    
    def print_table(self, data: List[Dict[str, Any]], title: str = "Enhanced Attack Chain Analysis"):
        """Print formatted table to console with enhanced information."""
        if not data:
            print("No data to display")
            return
            
        print(f"\n### {title}")
        print()
        
        # Print compact view first
        compact_data = []
        for row in data:
            compact_row = {
                'Stage': row['Stage'],
                'Tactic': row['Tactic (MITRE)'],
                'Technique': row['Technique'],
                'Tools': row['Associated Tools'][:50] + "..." if len(row['Associated Tools']) > 50 else row['Associated Tools'],
                'Confidence': row['Confidence']
            }
            compact_data.append(compact_row)
        
        # Print compact table
        headers = list(compact_data[0].keys())
        rows = [[row[header] for header in headers] for row in compact_data]
        table = tabulate(rows, headers=headers, tablefmt="grid", maxcolwidths=[10, 25, 30, 40, 10])
        print(table)
        
        # Print detailed information for each technique
        print("\n### Detailed Technique Analysis")
        print()
        
        for row in data:
            print(f"**{row['Stage']} - {row['Technique']}**")
            print(f"Description: {row['Description']}")
            print(f"Implementation: {row['Implementation Methods']}")
            print(f"Observed: {row['Observed Indicators']}")
            print(f"Confidence: {row['Confidence']}")
            print()
        
        # Print kill chain structure and attack paths
        self.print_kill_chain_structure()
        self.print_attack_paths()
    
    def save_csv(self, data: List[Dict[str, Any]], output_file: str):
        """Save tabular data to CSV file."""
        if not data:
            print("No data to save")
            return
            
        try:
            with open(output_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=data[0].keys())
                writer.writeheader()
                writer.writerows(data)
            print(f"CSV saved to: {output_file}")
        except Exception as e:
            print(f"Error saving CSV: {e}")
    
    def save_json(self, data: List[Dict[str, Any]], output_file: str):
        """Save tabular data to JSON file."""
        if not data:
            print("No data to save")
            return
            
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print(f"JSON saved to: {output_file}")
        except Exception as e:
            print(f"Error saving JSON: {e}")
    
    def process_campaign_file(self, input_file: str, output_dir: Optional[str] = None, 
                            save_csv: bool = False, save_json: bool = False, 
                            print_table: bool = True) -> List[Dict[str, Any]]:
        """Process a single campaign file and generate tabular data."""
        
        # Load RAF-AG data
        raf_data = self.load_raf_data(input_file)
        if not raf_data:
            return []
        
        # Generate tabular data
        tabular_data = self.generate_tabular_data(raf_data)
        
        # Extract campaign name from file path
        campaign_name = os.path.splitext(os.path.basename(input_file))[0]
        
        # Print table if requested
        if print_table:
            self.print_table(tabular_data, f"Enhanced Attack Chain Analysis - {campaign_name}")
        
        # Save files if requested
        if output_dir and (save_csv or save_json):
            os.makedirs(output_dir, exist_ok=True)
            
            if save_csv:
                csv_file = os.path.join(output_dir, f"{campaign_name}_attack_chain.csv")
                self.save_csv(tabular_data, csv_file)
            
            if save_json:
                json_file = os.path.join(output_dir, f"{campaign_name}_attack_chain.json")
                self.save_json(tabular_data, json_file)
        
        return tabular_data

def main():
    parser = argparse.ArgumentParser(description='ThreatPathMapper - Generate tabular attack chain data from RAF-AG results')
    parser.add_argument('input_file', help='Path to RAF-AG JSON result file')
    parser.add_argument('--output-dir', '-o', help='Output directory for saved files')
    parser.add_argument('--save-csv', action='store_true', help='Save results as CSV')
    parser.add_argument('--save-json', action='store_true', help='Save results as JSON')
    parser.add_argument('--no-print', action='store_true', help='Do not print table to console')
    
    args = parser.parse_args()
    
    # Validate input file
    if not os.path.exists(args.input_file):
        print(f"Error: Input file {args.input_file} does not exist")
        return
    
    # Create generator instance
    generator = AttackChainTableGenerator()
    
    # Process file
    generator.process_campaign_file(
        input_file=args.input_file,
        output_dir=args.output_dir,
        save_csv=args.save_csv,
        save_json=args.save_json,
        print_table=not args.no_print
    )

if __name__ == "__main__":
    main()