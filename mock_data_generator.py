#!/usr/bin/env python3
"""
Mock Data Generator for NSE Sovereign Extractor
Generates realistic synthetic annual report data for all 66 NSE companies.
Enables immediate testing of bulk ingestion, graph analysis, and drift detection.
"""

import json
import random
from pathlib import Path
from datetime import datetime, timedelta

OUTPUT_DIR = Path("nse_audit_data/mock_reports")
MANIFEST_FILE = Path("nse_audit_data/mock_manifest.json")

# Complete list of 66 NSE-listed companies (simplified for demo)
COMPANIES = [
    "Safaricom", "Equity Bank", "KCB Group", "EABL", "Co-operative Bank",
    "NCBA", "Standard Chartered", "Absa Bank", "Diamond Trust", "I&M Bank",
    "Family Bank", "Gtbank", "Spire Bank", "CFC Stanbic", "Barclays Kenya",
    "Britam", "Jubilee Holdings", "Sanlam Kenya", "Liberty Kenya", "CIC Insurance",
    "Kenya Re", "APA Insurance", "Directline Assurance", "Monarch Insurance", "Capitol Re",
    "Kenya Airways", "Bamburi Cement", "East African Portland", "Carbacid", "Mumias Sugar",
    "Chemical & Allied", "Kapchorua Tea", "Kakuzi", "Limuru Tea", "Williamson Tea",
    "Car & General", "DT Dobie", "Sameer Africa", "Scangroup", "Nation Media",
    "Media Max", "Standard Group", "Telkom Kenya", "Jamii Telecommunications", "Kenya Power",
    "Total Energies", "Vivo Energy", "Longhorn Publishers", "Centum Investment", "Acorn Holdings",
    "Argus", "Transcentury", "Uchumi Supermarkets", "BOC Gases", "Air Liquide",
    "British American Tobacco", "East African Malting", "Transnation", "Ritram", "Transcentury",
    "Homeaffairs", " transtec", "Transrail", "KenolKobil", "Oryx Energies",
    "Transcentury", "ILAM Fahari", "Stanlib Fahari", "Etica"
]

DIRECTOR_NAMES = [
    "Michael Turner", "Susan Kariuki", "James Mwangi", "Alice Munyua", "Peter Omondi",
    "Grace Wanjiru", "David Kimani", "Sarah Njeri", "John Kamau", "Elizabeth Mutua",
    "Robert Kipchoge", "Mary Akinyi", "Francis Wekesa", "Anne Cheptum", "Daniel arap",
    "Catherine Nyong'o", "Patrick Obath", "Lucy Ngugi", "Simon Chirchir", "Betty Maina",
    "Thomas Odhiambo", "Nancy Wambui", "George Anyona", "Priscilla Abwao", "Victor Okumu",
    "Diana Shikanda", "Brian Mudavadi", "Christine Ombaka", "Kenneth Matiba", "Wangari Maathai"
]

def generate_board_composition(year: int, company: str) -> dict:
    """Generate realistic board composition with some S.41/S.45 violations."""
    num_directors = random.randint(7, 15)
    
    # Ensure at least some are independent
    num_independent = random.randint(3, min(num_directors - 2, 8))
    
    directors = []
    base_year = year - random.randint(1, 15)  # Random appointment year
    
    for i in range(num_directors):
        name = random.choice(DIRECTOR_NAMES)
        is_independent = i < num_independent
        
        # Some directors have tenure > 9 years (S.45 violation)
        if random.random() < 0.3:  # 30% chance of long tenure
            appointment_year = base_year - random.randint(5, 15)
        else:
            appointment_year = base_year + random.randint(0, 5)
        
        tenure = year - appointment_year
        
        directors.append({
            "name": f"{name} {i}",
            "title": "Independent Non-Executive Director" if is_independent else "Executive Director",
            "is_independent": is_independent,
            "appointment_year": appointment_year,
            "tenure": tenure,
            "age": random.randint(45, 75)
        })
    
    return {
        "total_directors": num_directors,
        "independent_directors": num_independent,
        "ratio": round(num_independent / num_directors, 3),
        "complies_s41": num_independent / num_directors >= 0.333,
        "directors": directors
    }

def generate_related_parties(year: int, company: str) -> list:
    """Generate related party transactions with proper counterparties."""
    transactions = []
    
    num_transactions = random.randint(2, 8)
    
    for i in range(num_transactions):
        counterparty_type = random.choice([
            "Director-controlled entity",
            "Subsidiary company",
            "Associate company",
            "Key management personnel",
            "Pension fund"
        ])
        
        counterparty_name = f"{random.choice(['Alpha', 'Beta', 'Gamma', 'Delta'])} {counterparty_type.split()[0]} Ltd"
        
        amount = random.randint(10, 500) * 1_000_000  # 10M to 500M KES
        
        transactions.append({
            "counterparty": counterparty_name,
            "relationship": counterparty_type,
            "amount_kes": amount,
            "transaction_type": random.choice(["Consulting fees", "Loan", "Purchase of goods", "Service provision"]),
            "approved_by_board": random.choice([True, True, True, False]),  # 25% not approved
            "disclosed": True
        })
    
    return transactions

def generate_annual_report(company: str, year: int) -> dict:
    """Generate a complete mock annual report."""
    board = generate_board_composition(year, company)
    rpt = generate_related_parties(year, company)
    
    # Check for S.45 violations
    s45_violations = [d for d in board["directors"] if d["tenure"] > 9]
    
    return {
        "company": company,
        "year": year,
        "report_date": f"{year}-03-31",
        "governance": {
            "section_41": {
                "board_composition": board,
                "compliant": board["complies_s41"]
            },
            "section_45": {
                "violations": len(s45_violations),
                "violators": [{"name": d["name"], "tenure": d["tenure"]} for d in s45_violations],
                "compliant": len(s45_violations) == 0
            },
            "section_48": {
                "transactions": rpt,
                "total_value_kes": sum(t["amount_kes"] for t in rpt),
                "unapproved_transactions": len([t for t in rpt if not t["approved_by_board"]])
            }
        },
        "extracted_text_sample": f"Annual Report {year} - {company}. The Board comprises {board['independent_directors']} Independent Directors out of {board['total_directors']} total."
    }

def main():
    print("🏭 Generating Mock NSE Annual Reports...")
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    manifest = {}
    current_year = datetime.now().year
    
    for company in COMPANIES:
        company_dir = OUTPUT_DIR / company
        company_dir.mkdir(exist_ok=True)
        manifest[company] = []
        
        # Generate reports for last 3 years (for drift analysis)
        for year_offset in range(3):
            year = current_year - 1 - year_offset
            report = generate_annual_report(company, year)
            
            filename = f"{company}_Annual_Report_{year}.json"
            filepath = company_dir / filename
            
            with open(filepath, 'w') as f:
                json.dump(report, f, indent=2)
            
            manifest[company].append(str(filepath))
    
    # Save manifest
    with open(MANIFEST_FILE, 'w') as f:
        json.dump(manifest, f, indent=2)
    
    print(f"✅ Generated {len(COMPANIES) * 3} mock reports for {len(COMPANIES)} companies")
    print(f"📁 Location: {OUTPUT_DIR.absolute()}")
    print(f"📋 Manifest: {MANIFEST_FILE.absolute()}")
    
    # Show sample statistics
    print("\n📊 Sample Compliance Statistics:")
    s41_compliant = 0
    s45_compliant = 0
    total_rpt_value = 0
    
    for company in COMPANIES[:10]:  # Sample first 10
        report = generate_annual_report(company, current_year - 1)
        if report["governance"]["section_41"]["compliant"]:
            s41_compliant += 1
        if report["governance"]["section_45"]["compliant"]:
            s45_compliant += 1
        total_rpt_value += report["governance"]["section_48"]["total_value_kes"]
    
    print(f"   S.41 Compliance Rate: {s41_compliant}/10 ({s41_compliant*10}%)")
    print(f"   S.45 Compliance Rate: {s45_compliant}/10 ({s45_compliant*10}%)")
    print(f"   Avg RPT Value (sample): KES {total_rpt_value/10/1_000_000:.2f}M")

if __name__ == "__main__":
    main()
