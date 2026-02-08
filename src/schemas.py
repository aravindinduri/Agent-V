from typing import List, Optional
from pydantic import BaseModel, Field

class PolicyInfo(BaseModel):
    policy_number: Optional[str] = Field(None, description="The insurance policy number")
    policyholder_name: Optional[str] = Field(None, description="Name of the insured")
    effective_dates: Optional[str] = Field(None, description="Policy start and end dates")

class IncidentInfo(BaseModel):
    date: Optional[str] = Field(None, description="Date of the accident/loss")
    time: Optional[str] = Field(None, description="Time of the accident")
    location: Optional[str] = Field(None, description="City, State, or Street address")
    description: Optional[str] = Field(None, description="Description of how the loss occurred")

class InvolvedParty(BaseModel):
    name: Optional[str]
    role: Optional[str] = Field(None, description="e.g., Claimant, Third Party, Witness")
    contact: Optional[str]

class AssetDetails(BaseModel):
    asset_type: Optional[str] = Field(None, description="e.g., Vehicle, Property")
    asset_id: Optional[str] = Field(None, description="VIN, License Plate, or Property Address")
    estimated_damage: Optional[float] = Field(None, description="Numerical value of damage estimate")

class ExtractedData(BaseModel):
    policy_info: PolicyInfo
    incident_info: IncidentInfo
    involved_parties: List[InvolvedParty] = []
    asset_details: AssetDetails
    claim_type: Optional[str] = Field(None, description="e.g., Automobile, Property, Injury")
    # Helper to detect if 'injury' is mentioned in text even if claim_type isn't explicit
    has_injury_keywords: bool = False 
    # Helper to detect suspicious words
    suspicious_keywords: List[str] = []

# --- Final Output Model ---
class AgentOutput(BaseModel):
    extractedFields: dict
    missingFields: List[str]
    recommendedRoute: str
    reasoning: str