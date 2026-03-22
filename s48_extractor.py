#!/usr/bin/env python3
import re
import fitz  # PyMuPDF
import spacy
from pathlib import Path
from pydantic import BaseModel, Field, field_validator

# Load local NLP model
print("⏳ Loading local spaCy NLP model...")
nlp = spacy.load("en_core_web_sm")

class RelatedPartyTransaction(BaseModel):
    counterparty_name: str
    amount_kes: float

    @field_validator('counterparty_name')
    @classmethod
    def validate_counterparty(cls, v):
        generic_terms = ['market', 'total', 'turnover', 'shareholders', 'public', 'investors', 'board', 'directors']
        if any(term in v.lower() for term in generic_terms) or len(v.strip()) < 4:
            raise ValueError("Generic counterparty")
        return v.strip()

    @field_validator('amount_kes')
    @classmethod
    def validate_amount(cls, v):
        if v > 10_000_000_000:
            raise ValueError("Exceeds normal RPT bounds")
        return v

def extract_text_from_pdf(pdf_path: str) -> str:
    doc = fitz.open(pdf_path)
    return "".join(page.get_text() for page in doc)

def process_s48(pdf_path: str):
    print(f"\n📄 Processing: {pdf_path}")
    raw_text = extract_text_from_pdf(pdf_path)
    
    # Bounding Box Logic
    anchor_pattern = r"(?i)related\s+part(?:y|ies)\s+(?:transactions|disclosures|balances)"
    match = re.search(anchor_pattern, raw_text)
    
    if not match:
        print("⚠️ No Related Party section found.")
        return
        
    search_zone = raw_text[match.end():match.end() + 5000]
    print(f"✅ Bounding box locked: {len(search_zone)} characters.")
    
    # Semantic Parsing with spaCy
    print("🧠 Executing local NER extraction...")
    doc = nlp(search_zone)
    
    valid_transactions = []
    seen = set()

    for sent in doc.sents:
        orgs = [ent.text for ent in sent.ents if ent.label_ in ("ORG", "PERSON")]
        moneys = [ent.text for ent in sent.ents if ent.label_ in ("MONEY", "CARDINAL")]
        
        if orgs and moneys:
            counterparty = orgs[0].replace('\n', ' ')
            amount_str = moneys[0]
            
            clean_amount_str = re.sub(r'[^\d\.]', '', amount_str)
            if not clean_amount_str:
                continue
                
            amount_val = float(clean_amount_str)
            if 'billion' in amount_str.lower(): amount_val *= 1_000_000_000
            elif 'million' in amount_str.lower(): amount_val *= 1_000_000
            
            try:
                txn = RelatedPartyTransaction(
                    counterparty_name=counterparty,
                    amount_kes=amount_val
                )
                
                if txn.counterparty_name not in seen:
                    valid_transactions.append(txn)
                    seen.add(txn.counterparty_name)
            except ValueError:
                continue

    print("\n" + "="*50)
    print("S.48 RELATED PARTY TRANSACTIONS (SPACY NER)")
    print("="*50)
    if not valid_transactions:
        print("No valid transactions found within parameters.")
    else:
        for txn in valid_transactions:
            print(f"- {txn.counterparty_name}: KES {txn.amount_kes:,.2f}")
    print("="*50)

if __name__ == "__main__":
    target_file = Path("nse_data/nse_companies/nse_2023_annual_report.pdf")
    if target_file.exists():
        process_s48(str(target_file))
    else:
        print("⚠️ PDF not found. Ensure the path is correct.")
