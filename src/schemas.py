from typing import List, Optional, Union, Dict, Any 
from pydantic import BaseModel, Field

# --- Extraction Models ---
class PolicyInfo(BaseModel):
    policy_number: Optional[str] = Field(None, description="The insurance policy number")
    policyholder_name: Optional[str] = Field(None, description="Name of the insured")
    effective_dates: Optional[Union[str, Dict[str, Any]]] = Field(None, description="Policy start and end dates")

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
    estimated_damage: Optional[Union[float, str]] = Field(None, description="Damage amount") 

class ExtractedData(BaseModel):
    policy_info: PolicyInfo
    incident_info: IncidentInfo
    involved_parties: List[InvolvedParty] = []
    asset_details: AssetDetails
    claim_type: Optional[str] = Field(None, description="e.g., Automobile, Property, Injury")
    has_injury_keywords: bool = False 
    suspicious_keywords: List[str] = []

# --- Final Output Model ---
class AgentOutput(BaseModel):
    extractedFields: dict
    missingFields: List[str]
    recommendedRoute: str
    reasoning: str