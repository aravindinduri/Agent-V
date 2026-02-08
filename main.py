import os
import json
import glob
from dotenv import load_dotenv
from src.extractor import DeepSeekExtractor
from src.router import ClaimRouter

load_dotenv()

def main():
    # Initialize components
    extractor = DeepSeekExtractor()
    router = ClaimRouter()
    
    input_dir = "data/input"
    output_dir = "data/output"
    os.makedirs(output_dir, exist_ok=True)
    
    pdf_files = glob.glob(os.path.join(input_dir, "*.pdf"))
    
    print(f"Found {len(pdf_files)} documents to process.")

    for pdf_path in pdf_files:
        filename = os.path.basename(pdf_path)
        print(f"Processing {filename}...")
        
        try:
            # 1. Extract
            extracted_data = extractor.extract(pdf_path)
            
            # 2. Route
            final_decision = router.route(extracted_data)
            
            # 3. Save Output
            output_path = os.path.join(output_dir, f"{filename}.json")
            with open(output_path, 'w') as f:
                f.write(json.dumps(final_decision.model_dump(), indent=2))
                
            print(f" -> Done. Route: {final_decision.recommendedRoute}")
            
        except Exception as e:
            print(f" -> Failed to process {filename}: {str(e)}")

if __name__ == "__main__":
    main()