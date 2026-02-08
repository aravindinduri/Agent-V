
***

# 🛡️ Agent (V)

> **A Vision-Language powered agent that automates the First Notice of Loss (FNOL) process.**

## 📖 Overview


**Agent - V** automates this bottleneck. It uses **State-of-the-Art Vision Language Models (VLMs)** to "look" at the document (PDF/Image), extract structured data, validate it, and apply business logic to route the claim instantly.

### 🚀 Key Capabilities
*   **Multi-Modal Extraction:** Handles PDFs, JPGs, and PNGs (typed or handwritten).
*   **Intelligent Routing:**
    *    **Fast-track:** Clear liability, low damage (<$25k).
    *    **Investigation:** Detects fraud keywords ("staged", "suspicious").
    *    **Specialist:** Routes injury claims to senior adjusters.
    *    **Manual Review:** Flags missing mandatory data.
*   **Strict Validation:** Uses Pydantic to ensure AI output matches database schemas.

---

## 🧠 Engineering Thought Process & Architecture

Building this agent required specific architectural choices to ensure reliability and scalability. Here is why I built it this way:

### 1. Why Vision-Language Models (VLM) instead of OCR?
Traditional OCR (like Tesseract) extracts raw text but loses **spatial context**.
*   *OCR sees:* "Policy Number Name Date" (jumbled text).
*   *VLM sees:* "The text '12345' is located inside the box labeled 'Policy Number'."

We utilized **Qwen2.5-VL-7B-Instruct** (via Hugging Face API). This model acts as a "reasoning engine" that can look at a form layout and understand that a checked box next to "Bodily Injury" changes the entire workflow of the claim.

### 2. The JSON Consistency Challenge
LLMs are creative, which is bad for data entry. They might output "The date is 10/10/2023" one time and "October 10th" the next.
*   **Solution:** We use **Pydantic** models (`src/schemas.py`) to define a strict schema.
*   **Implementation:** The prompt explicitly requests JSON, and the Pydantic layer parses the output. If the model returns a dictionary for a date instead of a string, our schema validates and sanitizes it before it hits the application logic.

---

## 📂 Project Structure

```text
claims-agent/
├── data/
│   ├── input/              # Drop your raw PDFs/Images here
│   └── output/             # JSON results land here
├── src/
│   ├── extractor.py        # Connects to Hugging Face VLM
│   ├── router.py           # The "Brain": Business logic & rules engine
│   └── schemas.py          # Pydantic data models (The Source of Truth)
├── app.py                  # Streamlit User Interface
├── main.py                 # Batch processing script (CLI)
└── requirements.txt        # Dependencies
```

---

## 🛠️ Installation & Setup

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/claims-agent.git
cd claims-agent
```

### 2. Set up Environment
Create a virtual environment to keep dependencies clean:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

Install the required packages:
```bash
pip install -r requirements.txt
```
### 3. Configure Credentials
Create a `.env` file in the root directory. You will need a Hugging Face Access Token (Write permissions).

```env
HF_API_TOKEN=hf_your_token_here
# We use Qwen2.5-VL for its superior document understanding capabilities
HF_MODEL_ID=Qwen/Qwen2.5-VL-7B-Instruct
```

---

## 🖥️ Usage

### Option A: Interactive UI (Streamlit)
The best way to demo the agent. Visualizes the document alongside the extraction.

```bash
streamlit run app.py
```
*   Upload a document.
*   Watch the AI extract fields in real-time.
*   See the visual "Routing Decision" (Green/Red/Blue badges).

### Option B: Batch Processing (CLI)
Process a folder of documents at once.

1.  Place PDFs in `data/input/`.
2.  Run the script:
    ```bash
    python main.py
    ```
3.  Check `data/output/` for the resulting JSON files.

---

## 🧪 Sample Routing Logic
The `router.py` file implements the following decision tree:

| Condition | Route | Reasoning |
| :--- | :--- | :--- |
| **Description contains "fraud", "staged"** |  **Investigation** | Potential fraud detected. |
| **Missing Policy # or Date** |  **Manual Review** | Mandatory data missing. |
| **Claim Type = "Injury"** |  **Specialist** | High-risk claim. |
| **Damage < $25,000** | **Fast-track** | Low value, auto-approve candidate. |
| **Damage > $25,000** |  **Standard** | Standard claims adjuster flow. |

---

## 🔮 Future Improvements
*   **Human-in-the-loop:** Add a button in Streamlit to correct the extracted JSON and save it to a database.
*   **Database Integration:** Replace JSON file output with PostgreSQL.
*   **Confidence Scores:** Ask the model to return confidence (0-100%) for every field extracted to flag uncertain data.

### Screenshot
![Streamlit UI Demo](https://i.ibb.co/B5s54kWm/Screenshot-from-2026-02-09-01-46-53.png)
![Streamlit UI2](https://i.ibb.co/TnPdPTJ/Screenshot-from-2026-02-09-01-57-07.png)
****The Agent Dashboard analyzing a raw claim document. The agent extracts data via Vision-LLM, validates it against the schema, and automatically determines the 'Manual Review' route due to missing mandatory fields.****
---


