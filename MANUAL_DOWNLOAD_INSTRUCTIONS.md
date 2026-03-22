# Manual Download Instructions for Critical Documents

## Status: Automated Download Blocked

The following documents require **manual download** due to Cloudflare protection and SSL certificate restrictions on the server side.

---

## Document 1: Stima SACCO Annual Report 2023

**Why it matters:** This is Kenya's second-largest SACCO by assets (KES 59.1 billion, 200,000+ members). Running your extractor on this document proves the tool works on SACCO governance structures, not just NSE companies.

### Download Steps:

1. **Open your browser** and go to: `https://www.stima-sacco.com/publications/`

2. **Alternative direct URL:** `https://www.stima-sacco.com/download/annual-report-for-the-year-ended-31-december-2023/`

3. **Look for** "Annual Report for the Year Ended 31 December 2023" or similar

4. **Click the download button** - it should be a prominent button or link

5. **Save the file as:** `/workspace/nse_data/saccos_direct/Stima_SACCO_Annual_Report_2023.pdf`

6. **Verify the download:**
   ```bash
   cd /workspace
   ls -lh nse_data/saccos_direct/Stima_SACCO_Annual_Report_2023.pdf
   # Should be approximately 7-8 MB
   ```

### Expected File Size: ~7.73 MB

---

## Document 2: SASRA Guidance Note GG/2/2023

**Why it matters:** This document defines what SACCO governance compliance means under SASRA regulation. Section 11 contains the regulatory specification for the SACCO Pydantic schema. You cannot validate SACCO governance extraction without this.

### Download Steps:

1. **Open your browser** and go to: `https://www.sasra.go.ke`

2. **Navigate to:** Publications → Guidelines/Guidance Notes OR Resources

3. **Search for:** "Governance Guidance Note GG/2/2023" or "Guidance Note on Governance 2023"

4. **Alternative search terms:** 
   - "GG/2/2023"
   - "Governance Guidelines 2023"
   - "Deposit Taking SACCOs Governance"

5. **Download the PDF** and save as: `/workspace/nse_data/saccos_direct/SASRA_Guidance_Note_GG_2_2023.pdf`

6. **Verify the download:**
   ```bash
   cd /workspace
   ls -lh nse_data/saccos_direct/SASRA_Guidance_Note_GG_2_2023.pdf
   ```

### If Not Found on Website:

**Option A:** Contact SASRA directly
- Email: info@sasra.go.ke
- Request: "Governance Guidance Note GG/2/2023 for Deposit-Taking SACCOs"

**Option B:** Check these alternative locations:
- `https://www.sasra.go.ke/wp-content/uploads/2023/`
- `https://www.sasra.go.ke/resources/`
- `https://www.sasra.go.ke/regulatory-framework/`

---

## Document 3: SASRA Annual Supervision Report 2023

**Already Downloaded!** ✓

Location: `/workspace/nse_data/sasra_reports/SASRA_Supervision_Report_2023.pdf`
Size: 5.77 MB

This report lists every DT-SACCO with their compliance status. Use this for cross-reference validation.

---

## After Downloading: Next Steps

Once you have both documents downloaded:

### Step 1: Verify Files Are Valid PDFs
```bash
cd /workspace
python3 -c "
from pathlib import Path
for f in Path('nse_data/saccos_direct').glob('*.pdf'):
    if f.stat().st_size > 100000:  # > 100KB
        with open(f, 'rb') as pdf:
            header = pdf.read(8)
            print(f'{f.name}: {\"Valid PDF\" if header.startswith(b\"%PDF\") else \"INVALID\"} ({f.stat().st_size / 1_000_000:.2f} MB)')
"
```

### Step 2: Read Stima Report Manually (45 minutes)
Open the PDF and find:
- Board composition (how many members, roles)
- Committee structure (Audit, Credit, Education committees)
- CEO attendance at board meetings (voting or non-voting?)
- Related party loans to directors
- Independent governance audit status

Write down your findings in a text file as "ground truth".

### Step 3: Run the Extractor
Once the SACCO schema is built (see `sacco_schema.py`), run:
```bash
python3 run_sacco_extractor.py nse_data/saccos_direct/Stima_SACCO_Annual_Report_2023.pdf
```

### Step 4: Compare Results
Compare extractor output against your manual ground truth. Every discrepancy is a specific fix needed.

### Step 5: Cross-Reference with SASRA Supervision Report
Find Stima SACCO's entry in the SASRA 2023 Supervision Report. Does your tool's finding match the regulator's assessment?

---

## Why Manual Download Is Necessary

1. **Cloudflare Protection:** Stima Sacco uses Cloudflare which blocks automated requests
2. **SSL Certificate Issues:** SASRA's certificate doesn't match expected hostname from server environment
3. **JavaScript Rendering:** Both sites may require JavaScript to reveal download links

These protections are normal for financial institution websites and do not indicate any problem with your approach. The solution is simply to download once manually, then use the files for all development and testing.

---

## Timeline

- **Today:** Download both documents manually (15 minutes)
- **Today:** Read Stima report and create ground truth (45 minutes)  
- **Today:** Build SACCO schema (already provided in instructions)
- **Tomorrow:** Run extractor and compare results
- **This Week:** Show results to SACCO contact as proof of concept

---

## Contact Information for Assistance

If you cannot find the documents:

**Stima SACCO:**
- Website: https://www.stima-sacco.com
- Email: info@stima-sacco.com
- Phone: +254 20 2220606

**SASRA:**
- Website: https://www.sasra.go.ke
- Email: info@sasra.go.ke
- Phone: +254 20 2711939
