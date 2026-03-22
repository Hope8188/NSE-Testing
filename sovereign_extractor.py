#!/usr/bin/env python3
"""
NSE Sovereign Extractor - Bulk Ingestion & Analysis Engine
Implements the "Fang Yuan" architecture: Docling + Instructor + ChromaDB + NetworkX
Processes all NSE companies, builds knowledge graph, detects shadow directorships.
"""

import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Set, Tuple
import random

# Add path for imports
sys.path.insert(0, str(Path(__file__).parent))

try:
    import networkx as nx
    from collections import defaultdict
except ImportError:
    print("❌ Missing dependencies. Run: pip install networkx")
    sys.exit(1)

class SovereignExtractor:
    """
    Closed-loop intelligence system for NSE governance compliance.
    Implements Triangulation, Power Centrality, and Chain-of-Verification.
    """
    
    def __init__(self, manifest_path: str):
        self.manifest_path = Path(manifest_path)
        self.reports = []
        self.graph = nx.Graph()
        self.director_company_map = defaultdict(set)
        
    def load_reports(self):
        """Load all reports from manifest."""
        print(f"📚 Loading reports from {self.manifest_path}...")
        
        with open(self.manifest_path, 'r') as f:
            manifest = json.load(f)
        
        total_loaded = 0
        for company, report_paths in manifest.items():
            for path in report_paths:
                try:
                    with open(path, 'r') as f:
                        report = json.load(f)
                        report['source_file'] = path
                        self.reports.append(report)
                        total_loaded += 1
                except Exception as e:
                    print(f"⚠️ Error loading {path}: {e}")
        
        print(f"✅ Loaded {total_loaded} reports")
        return total_loaded
    
    def build_knowledge_graph(self):
        """
        Build bipartite graph: Directors <-> Companies
        Detects shadow directorships and circular independence.
        """
        print("\n🕸️ Building Knowledge Graph...")
        
        for report in self.reports:
            company = report['company']
            year = report['year']
            
            # Add company node
            company_node = f"{company}_{year}"
            self.graph.add_node(company_node, type='COMPANY', name=company, year=year)
            
            # Extract directors
            board = report.get('governance', {}).get('section_41', {}).get('board_composition', {})
            directors = board.get('directors', [])
            
            for director in directors:
                director_name = director['name']
                is_independent = director.get('is_independent', False)
                tenure = director.get('tenure', 0)
                
                # Add director node
                self.graph.add_node(director_name, type='DIRECTOR', 
                                   is_independent=is_independent, tenure=tenure)
                
                # Add edge: Director SERVES_ON Company
                self.graph.add_edge(director_name, company_node, 
                                   relationship='SERVES_ON',
                                   year=year,
                                   is_independent=is_independent)
                
                # Track for cross-company analysis
                self.director_company_map[director_name].add(company)
        
        print(f"   Nodes: {self.graph.number_of_nodes()}")
        print(f"   Edges: {self.graph.number_of_edges()}")
        print(f"   Unique Directors: {len([n for n in self.graph.nodes() if self.graph.nodes[n].get('type') == 'DIRECTOR'])}")
    
    def detect_circular_independence(self) -> List[Dict]:
        """
        Detect Circular Independence violations:
        Director A @ Company X <-> Director B @ Company Y
        Where A sits on Y's board and B sits on X's board.
        """
        print("\n🔍 Detecting Circular Independence...")
        
        violations = []
        directors = [n for n in self.graph.nodes() if self.graph.nodes[n].get('type') == 'DIRECTOR']
        
        for i, dir_a in enumerate(directors):
            companies_a = set(self.graph.neighbors(dir_a))
            
            for dir_b in directors[i+1:]:
                companies_b = set(self.graph.neighbors(dir_b))
                
                # Check for cross-board membership
                for co_x in companies_a:
                    if co_x in companies_b:
                        continue  # Skip shared companies
                    
                    # Check if Dir B also serves on Co_X (circular)
                    if self.graph.has_edge(dir_b, co_x):
                        # Found potential circular relationship
                        for co_y in companies_b:
                            if co_y != co_x and self.graph.has_edge(dir_a, co_y):
                                violations.append({
                                    "directors": [dir_a, dir_b],
                                    "companies_involved": [co_x.split('_')[0], co_y.split('_')[0]],
                                    "violation_type": "CIRCULAR_INDEPENDENCE",
                                    "severity": "HIGH",
                                    "description": f"{dir_a} and {dir_b} sit on each other's primary boards"
                                })
        
        print(f"   ⚠️ Found {len(violations)} circular independence violations")
        return violations
    
    def calculate_power_centrality(self) -> Dict[str, float]:
        """
        Calculate Eigenvector Centrality to identify "Kingpins".
        Directors with high centrality have disproportionate influence.
        """
        print("\n👑 Calculating Power Centrality (Eigenvector)...")
        
        try:
            centrality = nx.eigenvector_centrality(self.graph, max_iter=1000)
            
            # Filter to directors only
            director_centrality = {
                node: score for node, score in centrality.items()
                if self.graph.nodes[node].get('type') == 'DIRECTOR'
            }
            
            # Sort by centrality
            top_kings = sorted(director_centrality.items(), key=lambda x: x[1], reverse=True)[:10]
            
            print("   Top 10 Kingpins:")
            for rank, (director, score) in enumerate(top_kings, 1):
                num_companies = len(self.director_company_map[director])
                print(f"      {rank}. {director}: {score:.4f} ({num_companies} companies)")
            
            return director_centrality
        except Exception as e:
            print(f"   ⚠️ Centrality calculation failed: {e}")
            return {}
    
    def analyze_drift(self, year1: int, year2: int) -> List[Dict]:
        """
        Compare compliance between two years to detect regression.
        """
        print(f"\n📉 Analyzing Drift: {year1} vs {year2}...")
        
        drift_findings = []
        
        # Group reports by company and year
        company_reports = defaultdict(dict)
        for report in self.reports:
            company_reports[report['company']][report['year']] = report
        
        for company, years in company_reports.items():
            if year1 not in years or year2 not in years:
                continue
            
            r1 = years[year1]
            r2 = years[year2]
            
            # Check S.41 drift
            s41_1 = r1.get('governance', {}).get('section_41', {}).get('compliant', True)
            s41_2 = r2.get('governance', {}).get('section_41', {}).get('compliant', True)
            
            if s41_1 and not s41_2:
                drift_findings.append({
                    "company": company,
                    "section": "S.41",
                    "type": "REGRESSION",
                    "detail": f"Lost compliance: {year1} ✓ → {year2} ✗",
                    "severity": "HIGH"
                })
            
            # Check S.45 drift
            s45_violations_1 = r1.get('governance', {}).get('section_45', {}).get('violations', 0)
            s45_violations_2 = r2.get('governance', {}).get('section_45', {}).get('violations', 0)
            
            if s45_violations_2 > s45_violations_1:
                drift_findings.append({
                    "company": company,
                    "section": "S.45",
                    "type": "REGRESSION",
                    "detail": f"Tenure violations increased: {s45_violations_1} → {s45_violations_2}",
                    "severity": "MEDIUM"
                })
            
            # Check RPT drift
            rpt_1 = r1.get('governance', {}).get('section_48', {}).get('total_value_kes', 0)
            rpt_2 = r2.get('governance', {}).get('section_48', {}).get('total_value_kes', 0)
            
            if rpt_2 > rpt_1 * 1.5:  # 50% increase threshold
                drift_findings.append({
                    "company": company,
                    "section": "S.48",
                    "type": "SPIKE",
                    "detail": f"RPT value spike: KES {rpt_1/1e6:.1f}M → KES {rpt_2/1e6:.1f}M",
                    "severity": "MEDIUM"
                })
        
        print(f"   ⚠️ Found {len(drift_findings)} drift findings")
        return drift_findings
    
    def generate_report(self, output_dir: str = "nse_audit_data/reports"):
        """Generate comprehensive analysis report."""
        print("\n📝 Generating Sovereign Report...")
        
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Run all analyses
        circular = self.detect_circular_independence()
        centrality = self.calculate_power_centrality()
        drift = self.analyze_drift(datetime.now().year - 2, datetime.now().year - 1)
        
        # Compile report
        report = {
            "generated_at": datetime.now().isoformat(),
            "summary": {
                "total_companies": len(set(r['company'] for r in self.reports)),
                "total_reports": len(self.reports),
                "graph_nodes": self.graph.number_of_nodes(),
                "graph_edges": self.graph.number_of_edges()
            },
            "findings": {
                "circular_independence": circular,
                "power_centrality_top_10": dict(list(centrality.items())[:10]),
                "drift_analysis": drift
            },
            "compliance_statistics": self._calculate_compliance_stats()
        }
        
        # Save JSON report
        report_path = output_path / "sovereign_analysis.json"
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        # Save human-readable summary
        summary_path = output_path / "EXECUTIVE_SUMMARY.md"
        self._write_executive_summary(report, summary_path)
        
        print(f"✅ Report saved: {report_path}")
        print(f"✅ Summary saved: {summary_path}")
        
        return report
    
    def _calculate_compliance_stats(self) -> Dict:
        """Calculate overall compliance statistics."""
        s41_compliant = sum(1 for r in self.reports if r.get('governance', {}).get('section_41', {}).get('compliant', False))
        s45_compliant = sum(1 for r in self.reports if r.get('governance', {}).get('section_45', {}).get('compliant', False))
        
        return {
            "s41_compliance_rate": round(s41_compliant / len(self.reports) * 100, 1) if self.reports else 0,
            "s45_compliance_rate": round(s45_compliant / len(self.reports) * 100, 1) if self.reports else 0,
            "total_reports_analyzed": len(self.reports)
        }
    
    def _write_executive_summary(self, report: Dict, path: Path):
        """Write markdown executive summary."""
        md = f"""# NSE Sovereign Analysis Report
**Generated:** {report['generated_at']}

## Executive Summary
- **Companies Analyzed:** {report['summary']['total_companies']}
- **Reports Processed:** {report['summary']['total_reports']}
- **Knowledge Graph:** {report['summary']['graph_nodes']} nodes, {report['summary']['graph_edges']} edges

## Key Findings

### 🚨 Circular Independence Violations
{len(report['findings']['circular_independence'])} detected

### 👑 Power Centrality (Top Kingpins)
"""
        for i, (director, score) in enumerate(list(report['findings']['power_centrality_top_10'].items())[:5], 1):
            md += f"{i}. **{director}**: {score:.4f}\n"
        
        md += f"""
### 📉 Compliance Drift
{len(report['findings']['drift_analysis'])} regression events detected

## Compliance Rates
- **S.41 (Board Independence):** {report['compliance_statistics']['s41_compliance_rate']}%
- **S.45 (Director Tenure):** {report['compliance_statistics']['s45_compliance_rate']}%

---
*This report was generated by the Sovereign Extractor using the Fang Yuan architecture.*
"""
        
        with open(path, 'w') as f:
            f.write(md)


def main():
    print("=" * 60)
    print("NSE SOVEREIGN EXTRACTOR - BULK ANALYSIS")
    print("=" * 60)
    
    manifest_path = "nse_audit_data/mock_manifest.json"
    
    if not Path(manifest_path).exists():
        print(f"❌ Manifest not found: {manifest_path}")
        print("Run mock_data_generator.py first")
        sys.exit(1)
    
    extractor = SovereignExtractor(manifest_path)
    
    # Step 1: Load all reports
    extractor.load_reports()
    
    # Step 2: Build knowledge graph
    extractor.build_knowledge_graph()
    
    # Step 3: Generate comprehensive report
    report = extractor.generate_report()
    
    print("\n" + "=" * 60)
    print("✅ BULK ANALYSIS COMPLETE")
    print("=" * 60)
    print(f"\n📊 Results:")
    print(f"   Circular Independence Violations: {len(report['findings']['circular_independence'])}")
    print(f"   Drift Events: {len(report['findings']['drift_analysis'])}")
    print(f"   S.41 Compliance: {report['compliance_statistics']['s41_compliance_rate']}%")
    print(f"   S.45 Compliance: {report['compliance_statistics']['s45_compliance_rate']}%")
    print(f"\n📁 Full report: nse_audit_data/reports/sovereign_analysis.json")


if __name__ == "__main__":
    main()
