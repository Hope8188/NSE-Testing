# run_extraction.py
# Run: python3 run_extraction.py
# Takes 20-40 minutes. Saves results as JSON files.

import os
import json
import time
import re
from pathlib import Path
from datetime import datetime

# ── install check ──────────────────────────────────────────────
try:
    from google import genai
    from google.genai import types
except ImportError:
    import subprocess, sys
    subprocess.check_call([sys.executable, "-m", "pip", "install", "google-genai", "-q"])
    from google import genai
    from google.genai import types

from pydantic import BaseModel, Field
from typing import Optional, List, Literal

# ── API KEY ─────────────────────────────────────────────────────
API_KEY = None
env_file = Path("/workspace/.secure_env/.env")
if env_file.exists():
    for line in env_file.read_text().splitlines():
        if line.startswith("GEMINI_API_KEY="):
            API_KEY = line.split("=", 1)[1].strip()
if not API_KEY:
    API_KEY = os.environ.get("GEMINI_API_KEY")
if not API_KEY:
    raise ValueError("No GEMINI_API_KEY found")

client = genai.Client(api_key=API_KEY)
print(f"✅ Gemini client ready")

# ── OUTPUT DIRS ─────────────────────────────────────────────────
OUT_SACCO = Path("/workspace/extraction_results/saccos")
OUT_NSE   = Path("/workspace/extraction_results/nse")
OUT_SACCO.mkdir(parents=True, exist_ok=True)
OUT_NSE.mkdir(parents=True, exist_ok=True)

# ── DOCUMENT FILTERS ────────────────────────────────────────────
EXCLUDE_KEYWORDS = [
    "supervision report", "guidance note", "complaints",
    "policy", "circular", "regulation", "sasra annual",
    "guidance_note", "gg_2_2023", "complaints-management"
]

def is_sacco_annual_report(path: Path) -> bool:
    name = path.name.lower()
    if any(k in name for k in EXCLUDE_KEYWORDS):
        print(f"  SKIP (regulator doc): {path.name}")
        return False
    if path.stat().st_size < 500_000:  # under 500KB is suspicious
        print(f"  SKIP (too small): {path.name}")
        return False
    return True

def is_valid_nse_report(path: Path) -> bool:
    name = path.name
    # Must have a year >= 2016
    years = re.findall(r'(201[6-9]|202[0-9])', name)
    if not years:
        print(f"  SKIP (pre-2016 or no year): {path.name}")
        return False
    if path.stat().st_size < 500_000:
        print(f"  SKIP (too small): {path.name}")
        return False
    return True

def pick_diverse_nse(nse_dir: Path, n: int = 12) -> list:
    """Pick one file per company prefix, post-2016 only."""
    all_pdfs = [f for f in nse_dir.glob("*.pdf") if is_valid_nse_report(f)]
    seen = set()
    diverse = []
    for f in sorted(all_pdfs):
        prefix = f.name.split("_")[0].upper()
        if prefix not in seen:
            seen.add(prefix)
            diverse.append(f)
        if len(diverse) >= n:
            break
    return diverse

# ── SCHEMAS ─────────────────────────────────────────────────────
class SaccoBoardMember(BaseModel):
    name: str
    role: str
    is_elected: Optional[bool] = None
    is_independent: Optional[bool] = None
    attendance_rate: Optional[float] = None

class SaccoCommittee(BaseModel):
    name: str
    is_mandatory: bool
    exists: bool
    chairperson: Optional[str] = None
    member_count: Optional[int] = None
    meets_frequency: Optional[str] = None
    independent_majority: Optional[bool] = None

class SaccoResult(BaseModel):
    company_name: str
    reporting_year: int
    total_board_members: int
    board_members: List[SaccoBoardMember]
    audit_committee: SaccoCommittee
    credit_committee: SaccoCommittee
    supervisory_committee: Optional[SaccoCommittee] = None
    governance_committee: Optional[SaccoCommittee] = None
    independent_governance_audit_conducted: Optional[bool] = None
    governance_auditor_name: Optional[str] = None
    ceo_nonvoting_at_board: Optional[bool] = None
    conflict_of_interest_register_maintained: Optional[bool] = None
    related_party_loans_directors: Optional[float] = None
    related_party_loans_staff: Optional[float] = None
    related_party_loans_total_derived: Optional[float] = None
    related_party_disclosure_fragmented: bool = False
    compliance_score: float = Field(ge=0, le=100)
    compliance_gaps: List[str]
    confidence_level: Literal["CONFIRMED", "DERIVED", "FLAGGED_FOR_REVIEW"]
    evidence_pages: List[int]

class NseBoardMember(BaseModel):
    name: str
    role: str
    category: Literal["Executive", "Non-Executive", "Independent Non-Executive"]
    is_independent: bool
    tenure_years: Optional[int] = None

class NseCommittee(BaseModel):
    name: str
    exists: bool
    chairperson: Optional[str] = None
    independent_chair: Optional[bool] = None
    financial_expert_present: Optional[bool] = None
    meetings_held: Optional[int] = None

class NseResult(BaseModel):
    company_name: str
    reporting_year: int
    total_board_members: int
    board_members: List[NseBoardMember]
    independent_ratio: float
    independence_compliant: bool
    audit_committee: NseCommittee
    remuneration_committee: NseCommittee
    nomination_committee: NseCommittee
    risk_committee: Optional[NseCommittee] = None
    board_evaluation_conducted: bool
    external_evaluator_used: Optional[bool] = None
    ceo_name: Optional[str] = None
    top_5_executives_pay_disclosed: bool
    auditor_name: str
    auditor_opinion: str
    compliance_score: float = Field(ge=0, le=100)
    compliance_gaps: List[str]
    confidence_level: Literal["CONFIRMED", "DERIVED", "FLAGGED_FOR_REVIEW"]
    evidence_pages: List[int]

# ── EXTRACTION FUNCTION ──────────────────────────────────────────
def extract(pdf_path: Path, prompt: str, schema_class, out_dir: Path):
    out_file = out_dir / (pdf_path.stem + ".json")
    if out_file.exists():
        print(f"  ⏭  Already done: {pdf_path.name}")
        return True

    print(f"  📄 {pdf_path.name} ({pdf_path.stat().st_size/1e6:.1f} MB)")
    try:
        pdf_bytes = pdf_path.read_bytes()
        content = [
            types.Part.from_text(text=prompt),
            types.Part.from_bytes(data=pdf_bytes, mime_type="application/pdf")
        ]
        t0 = time.time()
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=content,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=schema_class,
                temperature=0.1,
            )
        )
        elapsed = round(time.time() - t0, 1)
        result = json.loads(response.text)
        result["source_file"] = pdf_path.name
        result["extraction_timestamp"] = datetime.now().isoformat()
        result["elapsed_seconds"] = elapsed
        out_file.write_text(json.dumps(result, indent=2))
        score = result.get("compliance_score", "?")
        gaps  = len(result.get("compliance_gaps", []))
        print(f"  ✅ Score: {score}/100 | Gaps: {gaps} | {elapsed}s → {out_file.name}")
        return True
    except Exception as e:
        print(f"  ❌ FAILED: {e}")
        err_file = out_dir / (pdf_path.stem + ".error.txt")
        err_file.write_text(str(e))
        return False

# ── PROMPTS ──────────────────────────────────────────────────────
SACCO_PROMPT = """
You are a governance auditor specialising in Kenya's SASRA regulatory framework.
Extract governance data from this SACCO annual report using the SASRA Guidance Note
GG/2/2023 as your compliance standard.

Key requirements to check:
- Board composition: total members, elected vs appointed, independence
- Mandatory committees: Audit Committee (independent majority required),
  Credit Committee, Supervisory Committee (statutory under Cooperative Act)
- CEO must attend board as non-voting participant
- Conflict of interest register must be maintained
- Independent governance audit must be conducted annually (Section 11.2)
- Related party loans: loans to directors and staff must be separately disclosed
- Mark related_party_disclosure_fragmented=true if director loans and staff loans
  are in separate line items rather than disclosed as a single total

Score 0-100 where 100 = fully compliant with all SASRA GG/2/2023 requirements.
For confidence_level: CONFIRMED = direct quote from document,
DERIVED = calculated from multiple items, FLAGGED_FOR_REVIEW = ambiguous.
"""

NSE_PROMPT = """
You are a governance auditor specialising in Kenya's NSE Corporate Governance Code 2015
and the POLD Regulations 2023.

Extract governance data from this NSE-listed company annual report.

Key requirements to check:
- Minimum one-third (33.3%) of board must be independent non-executive directors (S.41)
- Independent directors serving >9 years require shareholder approval (S.45)
- All related party transactions must disclose values and board/shareholder approval (S.48)
- Audit Committee must have independent majority and at least one financial expert
- Remuneration Committee must have independent chair
- Board evaluation must be conducted (external evaluator preferred)
- Top executive compensation must be disclosed

Score 0-100 where 100 = fully compliant with CG Code 2015 and POLD 2023.
For confidence_level: CONFIRMED = direct quote, DERIVED = calculated,
FLAGGED_FOR_REVIEW = ambiguous language.
"""

# ── MAIN ─────────────────────────────────────────────────────────
def main():
    # ── SACCO batch ──
    sacco_dir = Path("/workspace/nse_data/saccos_direct")
    print("\n" + "="*60)
    print("SACCO BATCH")
    print("="*60)

    sacco_files = [f for f in sacco_dir.glob("*.pdf") if is_sacco_annual_report(f)]
    print(f"Valid SACCO annual reports: {len(sacco_files)}")

    if len(sacco_files) == 0:
        print("⚠️  No valid SACCO annual reports found in", sacco_dir)
        print("   Looking in other locations...")
        # Try alternate location
        for alt in [Path("/workspace/nse_data/sasra_reports"),
                    Path("/workspace/nse_data/sacco_reports")]:
            if alt.exists():
                sacco_files = [f for f in alt.glob("*.pdf") if is_sacco_annual_report(f)]
                if sacco_files:
                    print(f"   Found {len(sacco_files)} files in {alt}")
                    break

    sacco_ok = sacco_fail = 0
    for f in sacco_files:
        ok = extract(f, SACCO_PROMPT, SaccoResult, OUT_SACCO)
        if ok: sacco_ok += 1
        else:  sacco_fail += 1
        time.sleep(2)  # rate limit

    # ── NSE batch ──
    nse_dir = Path("/workspace/nse_data/cma_reports")
    print("\n" + "="*60)
    print("NSE BATCH")
    print("="*60)

    nse_files = pick_diverse_nse(nse_dir, n=12)
    print(f"Diverse post-2016 NSE reports selected: {len(nse_files)}")
    for f in nse_files:
        print(f"  → {f.name}")

    nse_ok = nse_fail = 0
    for f in nse_files:
        ok = extract(f, NSE_PROMPT, NseResult, OUT_NSE)
        if ok: nse_ok += 1
        else:  nse_fail += 1
        time.sleep(2)

    # ── SUMMARY ──
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print(f"SACCO: {sacco_ok} success, {sacco_fail} failed")
    print(f"NSE:   {nse_ok} success, {nse_fail} failed")

    # Print scores table
    print("\nSCORES:")
    all_results = []
    for d, label in [(OUT_SACCO, "SACCO"), (OUT_NSE, "NSE")]:
        for f in sorted(d.glob("*.json")):
            try:
                data = json.loads(f.read_text())
                all_results.append({
                    "type": label,
                    "company": data.get("company_name", f.stem),
                    "year": data.get("reporting_year", "?"),
                    "score": data.get("compliance_score", 0),
                    "gaps": len(data.get("compliance_gaps", [])),
                    "confidence": data.get("confidence_level", "?")
                })
            except:
                pass

    all_results.sort(key=lambda x: x["score"])
    for r in all_results:
        print(f"  [{r['type']}] {r['company']} {r['year']}: "
              f"{r['score']}/100 | {r['gaps']} gaps | {r['confidence']}")

    if all_results:
        lowest  = all_results[0]
        highest = all_results[-1]
        print(f"\n🔴 LOWEST:  {lowest['company']} — {lowest['score']}/100")
        print(f"🟢 HIGHEST: {highest['company']} — {highest['score']}/100")
        print(f"\nNext step: manually verify the lowest scorer against")
        print(f"SASRA/CMA enforcement data for concordance proof.")

    print(f"\nResults saved to:")
    print(f"  {OUT_SACCO}")
    print(f"  {OUT_NSE}")

if __name__ == "__main__":
    main()
