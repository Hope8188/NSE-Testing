#!/usr/bin/env python3
"""
SACCO Governance Schema per SASRA Guidance Note GG/2/2023 Section 11.
This schema is completely different from NSE CG Code S.41/45/48.

Key differences from NSE:
- SACCO boards are elected by members, not appointed independent directors
- Mandatory committees: Audit, Credit, Education (not just Audit & Risk)
- CEO attends board as non-voting participant
- Focus on related party LENDING (not just transactions)
- Independent governance audit required annually
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum


class SACCOBoardRole(str, Enum):
    """SACCO board roles under cooperative law."""
    CHAIRMAN = "Chairman"
    VICE_CHAIR = "Vice-Chair"
    SECRETARY = "Secretary"
    TREASURER = "Treasurer"
    MEMBER = "Member"
    UNKNOWN = "Unknown"


class SACCOCommitteeType(str, Enum):
    """Mandatory and optional SACCO committees per SASRA."""
    AUDIT = "Audit Committee"
    CREDIT = "Credit Committee"
    EDUCATION = "Education Committee"
    FINANCE = "Finance Committee"
    SUPERVISORY = "Supervisory Committee"
    GOVERNANCE = "Governance Committee"
    RISK = "Risk Committee"
    OTHER = "Other"


class SACCOBoardMember(BaseModel):
    """
    A SACCO board member - elected by members, not appointed.
    
    SASRA GG/2/2023 Section 11.1: Board composition requirements.
    """
    name: str = Field(
        description="Full name of the board member"
    )
    role: SACCOBoardRole = Field(
        description="Position held: Chairman, Vice-Chair, Secretary, Treasurer, or Member"
    )
    is_elected: Optional[bool] = Field(
        default=None,
        description="Whether this member was elected by SACCO members (vs appointed)"
    )
    appointment_year: Optional[int] = Field(
        default=None,
        description="Year when this member joined the board"
    )
    term_end_year: Optional[int] = Field(
        default=None,
        description="Year when current term ends"
    )
    is_independent: Optional[bool] = Field(
        default=None,
        description="Whether member qualifies as independent (rare in SACCOs)"
    )
    gender: Optional[str] = Field(
        default=None,
        description="Gender for diversity reporting"
    )
    
    class Config:
        use_enum_values = True


class SACCOCommittee(BaseModel):
    """
    SACCO committee structure per SASRA requirements.
    
    Key difference from NSE: SACCOs must have Credit Committee and Education Committee
    in addition to Audit Committee. CEO may attend but cannot vote.
    """
    name: SACCOCommitteeType = Field(
        description="Committee name/type"
    )
    exists: bool = Field(
        description="Whether this committee exists and is active"
    )
    member_count: Optional[int] = Field(
        default=None,
        description="Number of committee members"
    )
    chairperson: Optional[str] = Field(
        default=None,
        description="Name of committee chairperson"
    )
    meets_required_frequency: Optional[bool] = Field(
        default=None,
        description="Whether committee met the minimum required times per year"
    )
    meetings_held: Optional[int] = Field(
        default=None,
        description="Number of meetings held in the reporting year"
    )
    quorum_compliance: Optional[bool] = Field(
        default=None,
        description="Whether all meetings had proper quorum"
    )
    ceo_attends: Optional[bool] = Field(
        default=None,
        description="Whether CEO attends committee meetings (non-voting)"
    )
    
    class Config:
        use_enum_values = True


class SACCORelatedPartyLoan(BaseModel):
    """
    Disclosure of loans to board members and senior staff.
    
    Critical difference from NSE: SACCOs LEND to members (including directors),
    while NSE companies typically disclose TRANSACTIONS with related parties.
    
    SASRA GG/2/2023 Section 11.3: Related party lending restrictions.
    """
    recipient_name: Optional[str] = Field(
        default=None,
        description="Name of the borrower (director or senior staff)"
    )
    recipient_role: Optional[str] = Field(
        default=None,
        description="Role of borrower (e.g., 'Board Member', 'CEO', 'CFO')"
    )
    loan_amount: Optional[float] = Field(
        default=None,
        description="Outstanding loan amount in KES"
    )
    loan_purpose: Optional[str] = Field(
        default=None,
        description="Purpose of the loan"
    )
    interest_rate: Optional[float] = Field(
        default=None,
        description="Interest rate charged (% per annum)"
    )
    is_at_market_terms: Optional[bool] = Field(
        default=None,
        description="Whether loan terms are at market rates"
    )
    approval_disclosed: Optional[bool] = Field(
        default=None,
        description="Whether loan was approved with interested party recused"
    )


class SACCOGovernanceResult(BaseModel):
    """
    Complete SACCO governance extraction result.
    
    Based on SASRA Guidance Note GG/2/2023 Section 11:
    \"Governance Requirements for Deposit-Taking SACCOs\"
    
    This is COMPLETELY DIFFERENT from NSE Corporate Governance Code.
    Do NOT use NSE schemas for SACCO documents.
    """
    
    # === BOARD COMPOSITION ===
    total_board_members: int = Field(
        description="Total number of board directors"
    )
    board_members: List[SACCOBoardMember] = Field(
        default_factory=list,
        description="List of all board members with their roles"
    )
    
    # Gender diversity (SASRA requirement)
    male_directors: Optional[int] = Field(
        default=None,
        description="Number of male board members"
    )
    female_directors: Optional[int] = Field(
        default=None,
        description="Number of female board members"
    )
    gender_diversity_compliant: Optional[bool] = Field(
        default=None,
        description="Whether board meets SASRA gender diversity rules (max 2/3 same gender)"
    )
    
    # === MANDATORY COMMITTEES ===
    audit_committee: Optional[SACCOCommittee] = Field(
        default=None,
        description="Audit Committee - REQUIRED by SASRA"
    )
    credit_committee: Optional[SACCOCommittee] = Field(
        default=None,
        description="Credit Committee - REQUIRED by SASRA (unique to SACCOs)"
    )
    education_committee: Optional[SACCOCommittee] = Field(
        default=None,
        description="Education Committee - REQUIRED by SASRA (unique to SACCOs)"
    )
    supervisory_committee: Optional[SACCOCommittee] = Field(
        default=None,
        description="Supervisory Committee - some SACCOs have this"
    )
    finance_committee: Optional[SACCOCommittee] = Field(
        default=None,
        description="Finance Committee - optional"
    )
    
    # === CEO GOVERNANCE RELATIONSHIP ===
    ceo_name: Optional[str] = Field(
        default=None,
        description="Name of the CEO/Managing Director"
    )
    ceo_nonvoting_at_board: Optional[bool] = Field(
        default=None,
        description="CEO attends board meetings without voting rights (SASRA requirement)"
    )
    ceo_also_board_chair: Optional[bool] = Field(
        default=None,
        description="Whether CEO also serves as Board Chair (generally discouraged)"
    )
    
    # === KEY SASRA COMPLIANCE CHECKS ===
    conflict_of_interest_register_maintained: Optional[bool] = Field(
        default=None,
        description="Whether SACCO maintains a conflict of interest register"
    )
    independent_governance_audit_conducted: Optional[bool] = Field(
        default=None,
        description="GG/2/2023 Section 11.2: Annual independent governance audit conducted"
    )
    electoral_policy_approved_by_members: Optional[bool] = Field(
        default=None,
        description="Whether electoral policy was approved by AGM"
    )
    compensation_policy_approved_by_members: Optional[bool] = Field(
        default=None,
        description="Whether director compensation policy was approved by AGM"
    )
    
    # === BOARD MEETINGS ===
    board_meetings_held: Optional[int] = Field(
        default=None,
        description="Number of board meetings held in the year"
    )
    board_meeting_quorum_compliance: Optional[bool] = Field(
        default=None,
        description="Whether all board meetings had proper quorum"
    )
    average_director_attendance: Optional[float] = Field(
        default=None,
        description="Average attendance rate across all directors (%)"
    )
    
    # === RELATED PARTY LENDING ===
    loans_to_board_members_disclosed: Optional[bool] = Field(
        default=None,
        description="Whether loans to directors are disclosed"
    )
    total_loans_to_directors: Optional[float] = Field(
        default=None,
        description="Total outstanding loans to all board members in KES"
    )
    loans_to_staff_disclosed: Optional[bool] = Field(
        default=None,
        description="Whether loans to senior staff are disclosed"
    )
    related_party_loans: List[SACCORelatedPartyLoan] = Field(
        default_factory=list,
        description="Detailed list of related party loans"
    )
    
    # === EVIDENCE ===
    evidence_quote: str = Field(
        description="Direct quote from the annual report supporting the findings"
    )
    evidence_page: Optional[int] = Field(
        default=None,
        description="Page number where evidence was found"
    )
    evidence_section: Optional[str] = Field(
        default=None,
        description="Section title where evidence was found"
    )
    
    # === COMPLIANCE VERDICT ===
    @property
    def passes_sasra_minimum(self) -> bool:
        """
        Check if SACCO meets minimum SASRA governance requirements.
        
        Per GG/2/2023 Section 11, minimum requirements are:
        1. Audit Committee exists
        2. Credit Committee exists  
        3. Education Committee exists
        4. Independent governance audit conducted
        5. Gender diversity compliance (not more than 2/3 same gender)
        """
        checks = [
            self.audit_committee and self.audit_committee.exists,
            self.credit_committee and self.credit_committee.exists,
            self.education_committee and self.education_committee.exists,
            self.independent_governance_audit_conducted is True,
        ]
        return all(checks)
    
    @property
    def compliance_score(self) -> float:
        """
        Calculate overall compliance score (0.0 to 1.0).
        
        Higher score = better governance practices.
        """
        checks = []
        
        # Board structure (20%)
        checks.append(self.total_board_members >= 5)  # Minimum board size
        checks.append(len(self.board_members) > 0)
        
        # Committees (40%)
        checks.append(self.audit_committee and self.audit_committee.exists)
        checks.append(self.credit_committee and self.credit_committee.exists)
        checks.append(self.education_committee and self.education_committee.exists)
        
        # Meetings (15%)
        checks.append(self.board_meetings_held and self.board_meetings_held >= 4)
        checks.append(self.board_meeting_quorum_compliance is True)
        
        # Compliance items (25%)
        checks.append(self.conflict_of_interest_register_maintained is True)
        checks.append(self.independent_governance_audit_conducted is True)
        checks.append(self.gender_diversity_compliant is True)
        
        # Transparency (optional bonus)
        checks.append(self.loans_to_board_members_disclosed is True)
        
        passed = sum(1 for c in checks if c)
        return round(passed / len(checks), 2)
    
    def get_compliance_gaps(self) -> List[str]:
        """Return list of specific compliance gaps identified."""
        gaps = []
        
        if not (self.audit_committee and self.audit_committee.exists):
            gaps.append("Missing Audit Committee")
        
        if not (self.credit_committee and self.credit_committee.exists):
            gaps.append("Missing Credit Committee (SASRA requirement)")
        
        if not (self.education_committee and self.education_committee.exists):
            gaps.append("Missing Education Committee (SASRA requirement)")
        
        if self.independent_governance_audit_conducted is not True:
            gaps.append("No independent governance audit conducted")
        
        if self.gender_diversity_compliant is False:
            gaps.append("Gender diversity non-compliant (max 2/3 same gender)")
        
        if self.board_meetings_held and self.board_meetings_held < 4:
            gaps.append(f"Insufficient board meetings ({self.board_meetings_held}/year, minimum 4)")
        
        if self.conflict_of_interest_register_maintained is not True:
            gaps.append("No conflict of interest register maintained")
        
        if self.ceo_also_board_chair is True:
            gaps.append("CEO also serves as Board Chair (poor governance practice)")
        
        return gaps
    
    class Config:
        use_enum_values = True
        json_schema_extra = {
            "description": "SACCO governance extraction per SASRA GG/2/2023 Section 11",
            "example": {
                "total_board_members": 9,
                "board_members": [
                    {"name": "John Doe", "role": "Chairman"},
                    {"name": "Jane Smith", "role": "Vice-Chair"}
                ],
                "audit_committee": {"name": "Audit Committee", "exists": True, "member_count": 4},
                "credit_committee": {"name": "Credit Committee", "exists": True, "member_count": 5},
                "education_committee": {"name": "Education Committee", "exists": True, "member_count": 3},
                "ceo_nonvoting_at_board": True,
                "independent_governance_audit_conducted": True,
                "gender_diversity_compliant": True,
                "evidence_quote": "The Society has 9 board members...",
                "evidence_page": 45
            }
        }


# === CONVENIENCE FUNCTIONS ===

def create_empty_sacco_result() -> SACCOGovernanceResult:
    """Create an empty SACCO governance result template."""
    return SACCOGovernanceResult(
        total_board_members=0,
        board_members=[],
        evidence_quote="",
        audit_committee=SACCOCommittee(name=SACCOCommitteeType.AUDIT, exists=False),
        credit_committee=SACCOCommittee(name=SACCOCommitteeType.CREDIT, exists=False),
        education_committee=SACCOCommittee(name=SACCOCommitteeType.EDUCATION, exists=False),
    )


def validate_sacco_result(result: SACCOGovernanceResult) -> dict:
    """
    Validate a SACCO governance result and return detailed feedback.
    
    Returns:
        dict with keys: 'valid', 'warnings', 'errors', 'compliance_score'
    """
    warnings = []
    errors = []
    
    # Required fields
    if result.total_board_members < 1:
        errors.append("Must have at least 1 board member")
    
    if not result.evidence_quote:
        errors.append("Missing evidence quote")
    
    # Warnings for common issues
    if result.total_board_members < 5:
        warnings.append(f"Small board size ({result.total_board_members}), SASRA recommends 5-9")
    
    if result.board_meetings_held and result.board_meetings_held < 4:
        warnings.append(f"Only {result.board_meetings_held} board meetings, minimum is 4")
    
    if result.gender_diversity_compliant is False:
        warnings.append("Gender diversity non-compliant")
    
    gaps = result.get_compliance_gaps()
    if gaps:
        warnings.extend(gaps)
    
    return {
        'valid': len(errors) == 0,
        'warnings': warnings,
        'errors': errors,
        'compliance_score': result.compliance_score,
        'passes_sasra_minimum': result.passes_sasra_minimum
    }


if __name__ == "__main__":
    # Test the schema
    test_result = create_empty_sacco_result()
    print("Empty SACCO result created successfully")
    print(f"Passes SASRA minimum: {test_result.passes_sasra_minimum}")
    print(f"Compliance score: {test_result.compliance_score}")
    
    validation = validate_sacco_result(test_result)
    print(f"\nValidation: {validation}")
