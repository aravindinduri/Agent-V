from src.schemas import ExtractedData, AgentOutput

class ClaimRouter:
    def __init__(self):
        self.mandatory_fields = [
            ("policy_info.policy_number", "Policy Number"),
            ("policy_info.policyholder_name", "Policyholder Name"),
            ("incident_info.date", "Date of Loss"),
            ("incident_info.description", "Incident Description"),
            ("asset_details.asset_type", "Asset Type")
        ]

    def _get_nested_value(self, obj, path):
        try:
            for part in path.split('.'):
                obj = getattr(obj, part)
            return obj
        except AttributeError:
            return None

    def route(self, data: ExtractedData) -> AgentOutput:
        missing_fields = []
        
        for path, label in self.mandatory_fields:
            val = self._get_nested_value(data, path)
            if not val or val == "null":
                missing_fields.append(label)
    
        # Convert estimated_damage to float
        damage = data.asset_details.estimated_damage
        if isinstance(damage, str):
            try:
                damage = float(damage.replace(",", "").replace(" ", ""))
            except ValueError:
                damage = None
    
        route = ""
        reasoning = ""
        
        # Priority 1: Investigation (Fraud indicators)
        if data.suspicious_keywords:
            route = "Investigation Flag"
            reasoning = f"Suspicious keywords detected: {', '.join(data.suspicious_keywords)}"
    
        # Priority 2: Manual Review (Missing Data)
        elif missing_fields:
            route = "Manual Review"
            reasoning = f"Mandatory fields missing: {', '.join(missing_fields)}"
    
        # Priority 3: Specialist (Injury)
        elif data.has_injury_keywords or (data.claim_type and "injury" in data.claim_type.lower()):
            route = "Specialist Queue"
            reasoning = "Bodily injury indicated in claim type or description."
    
        # Priority 4: Fast-track (Low Value)
        elif damage is not None and damage < 25000:
            route = "Fast-track"
            reasoning = f"Estimated damage (${damage}) is under the $25,000 threshold."
        else:
            route = "Standard Processing"
            reasoning = "Claim exceeds fast-track limits but contains all mandatory info."

        return AgentOutput(
            extractedFields=data.dict(),
            missingFields=missing_fields,
            recommendedRoute=route,
            reasoning=reasoning
        )