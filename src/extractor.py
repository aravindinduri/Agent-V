import os
import json
import base64
from io import BytesIO
from PIL import Image
from pdf2image import convert_from_path
from huggingface_hub import InferenceClient
from src.schemas import ExtractedData

class DeepSeekExtractor:
    def __init__(self):
        self.token = os.getenv("HF_API_TOKEN")
        self.model_id = os.getenv("HF_MODEL_ID")
        self.client = InferenceClient(token=self.token)

    def _load_document(self, file_path: str):
        """Loads a PDF or Image from path and returns a PIL Image."""
        ext = os.path.splitext(file_path)[1].lower()
        
        if ext == '.pdf':
            images = convert_from_path(file_path, first_page=1, last_page=1)
            return images[0] if images else None
        elif ext in ['.jpg', '.jpeg', '.png']:
            # Load image directly
            return Image.open(file_path)
        else:
            raise ValueError(f"Unsupported file format: {ext}")

    def _image_to_base64(self, image):
        buffered = BytesIO()
        # Convert to RGB to handle PNG transparency issues
        if image.mode != 'RGB':
            image = image.convert('RGB')
        image.save(buffered, format="JPEG")
        return base64.b64encode(buffered.getvalue()).decode("utf-8")

    def extract(self, file_path: str) -> ExtractedData:
        image = self._load_document(file_path)
        if not image:
            raise ValueError("Could not process document image")

        # Prompt optimized for Qwen2.5-VL / DeepSeek-VL
        prompt = """
        Analyze this insurance document. Extract the following fields into valid JSON:
        
        {
          "policy_info": { "policy_number": null, "policyholder_name": null, "effective_dates": null },
          "incident_info": { "date": null, "time": null, "location": null, "description": null },
          "involved_parties": [ { "name": null, "role": null, "contact": null } ],
          "asset_details": { "asset_type": null, "asset_id": null, "estimated_damage": null },
          "claim_type": null,
          "has_injury_keywords": false,
          "suspicious_keywords": []
        }

        Rules:
        - If a value is missing, use null.
        - Check description for suspicious words like "fraud", "staged".
        - Return ONLY the JSON object. No markdown.
        """

        try:
            response = self.client.chat_completion(
                model=self.model_id,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{self._image_to_base64(image)}"}},
                            {"type": "text", "text": prompt}
                        ]
                    }
                ],
                max_tokens=1000
            )
            
            raw_content = response.choices[0].message.content
            clean_text = raw_content.replace("```json", "").replace("```", "").strip()
            return self._clean_and_parse_json(clean_text)

        except Exception as e:
            print(f"API Error: {e}")
            # Return empty structure on failure
            return ExtractedData(
                policy_info={}, incident_info={}, asset_details={}
            )

    def _clean_and_parse_json(self, raw_text: str) -> ExtractedData:
        try:
            data_dict = json.loads(raw_text)
            return ExtractedData(**data_dict)
        except Exception:
            print("JSON Parsing failed. Raw output:", raw_text)
            return ExtractedData(policy_info={}, incident_info={}, asset_details={})