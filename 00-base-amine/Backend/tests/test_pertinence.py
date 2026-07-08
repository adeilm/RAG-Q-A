"""
test_pertinence.py — Pertinence Test Suite (M2 - Task 6)
═══════════════════════════════════════════════════════════════════════════════
This suite runs a set of "Golden Q&A" cases against the RAG engine.
It uses an LLM-as-a-judge to evaluate if the answer is correct based on the expected facts.
It generates a CSV report (pertinence_report.csv) for management review.

Run:
  pytest tests/test_pertinence.py -v -s
═══════════════════════════════════════════════════════════════════════════════
"""

import csv
import json
import pathlib
import uuid
import time
from typing import List, Dict
import pytest
from fastapi.testclient import TestClient

from main import app
from services.llm_client import call_llm

client = TestClient(app, raise_server_exceptions=True)

# ── Unique test-run credentials ───────────────────────────────────────────────
_RUN_ID       = uuid.uuid4().hex[:8]
TEST_EMAIL    = f"pertinence_{_RUN_ID}@bimlo-test.local"
TEST_USERNAME = f"pertinence_{_RUN_ID}"
TEST_PASSWORD = "pytest_password_123"

# ── 1. The Golden Dataset ─────────────────────────────────────────────────────
# We are using dummy questions based on the regression test document until
# real PDFs and questions are provided by the CEO.
GOLDEN_TEST_CASES = [
    {
        "id": "TC-01",
        "question": "What is the downstream bandwidth of a GPON node?",
        "expected_facts": ["2.488 Gbps"],
        "expected_document": "test_doc.txt"
    },
    {
        "id": "TC-02",
        "question": "What frequencies does 5G NR use?",
        "expected_facts": ["millimeter-wave", "mmWave", "above 24 GHz"],
        "expected_document": "test_doc.txt"
    },
    {
        "id": "TC-03",
        "question": "What does LOD 300 represent in BIM?",
        "expected_facts": ["construction-document level detail"],
        "expected_document": "test_doc.txt"
    },
    {
        "id": "TC-04",
        "question": "What is the purpose of the BIMLO Copilot?",
        "expected_facts": ["transform a base of completed projects into an AI assistant"],
        "expected_document": "CAHIER_DES_CHARGES_BIMLO_RAG_Copilot.docx" 
    }
]

# ── 2. LLM Evaluator Prompt ───────────────────────────────────────────────────
JUDGE_PROMPT_TEMPLATE = """
You are an expert evaluator for an AI RAG system.
Your job is to determine if the generated answer is CORRECT and COMPLETE based ONLY on whether it contains the expected facts.

QUESTION ASKED:
{question}

EXPECTED FACTS THAT MUST BE PRESENT:
{expected_facts}

GENERATED ANSWER:
{generated_answer}

Respond ONLY with a valid JSON object in this exact format:
{{
    "passed": true,
    "reasoning": "A short explanation of why it passed or failed"
}}
"""

def evaluate_answer(question: str, expected_facts: List[str], generated_answer: str) -> Dict:
    """Uses LLM-as-a-judge to grade the answer."""
    prompt = JUDGE_PROMPT_TEMPLATE.format(
        question=question,
        expected_facts=json.dumps(expected_facts),
        generated_answer=generated_answer
    )
    
    try:
        # Call the LLM using the shared client
        result_str = call_llm(
            prompt=prompt,
            system_prompt="You are a strict technical evaluator. Output only valid JSON.",
            task="classify",
            max_tokens=150,
            temperature=0.0
        )
        # Parse JSON
        result_str = result_str.strip().strip("```json").strip("```").strip()
        result = json.loads(result_str)
        return {
            "passed": bool(result.get("passed", False)),
            "reasoning": result.get("reasoning", "Parse error")
        }
    except Exception as e:
        print(f"⚠️ Judge Evaluation Failed: {e}")
        return {"passed": False, "reasoning": f"Judge error: {str(e)}"}


def _auth(token: str) -> Dict[str, str]:
    return {"Authorization": f"Bearer {token}"}

# ── 3. The Test Suite ─────────────────────────────────────────────────────────

@pytest.fixture(scope="module")
def auth_token():
    """Register and login a test user, return the token."""
    res = client.post("/auth/signup", json={
        "email": TEST_EMAIL,
        "username": TEST_USERNAME,
        "password": TEST_PASSWORD,
    })
    assert res.status_code == 200, f"Signup failed: {res.text}"
    return res.json()["token"]


def test_pertinence_suite(auth_token):
    """Run all golden test cases, evaluate them, and generate a CSV report."""
    print("\n\n" + "="*80)
    print("🏃 RUNNING PERTINENCE TEST SUITE")
    print("="*80 + "\n")
    
    session_id = uuid.uuid4().hex
    results = []
    passed_count = 0
    
    csv_path = pathlib.Path(__file__).parent.parent / "pertinence_report.csv"
    
    with open(csv_path, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["Test ID", "Question", "Expected Facts", "Expected Document", "Generated Answer", "Passed", "Reasoning", "Actual Sources"])
        
        for case in GOLDEN_TEST_CASES:
            print(f"\n🧪 Executing {case['id']}: {case['question']}")
            
            # Send the query to the RAG engine
            body = {
                "query": case["question"], 
                "top_k": 3, 
                "session_id": session_id,
                "force_route": "rag" # Force standard RAG to avoid bypassing retrieval
            }
            start_time = time.time()
            res = client.post("/query", json=body, headers=_auth(auth_token))
            duration = time.time() - start_time
            
            if res.status_code != 200:
                print(f"❌ API Error: {res.text}")
                continue
                
            data = res.json()
            generated_answer = data.get("answer", "")
            sources = data.get("sources", [])
            actual_filenames = [s.get("filename", "unknown") for s in sources]
            
            # Evaluate using LLM-as-a-judge
            evaluation = evaluate_answer(case["question"], case["expected_facts"], generated_answer)
            passed = evaluation["passed"]
            reasoning = evaluation["reasoning"]
            
            # Check if expected document was retrieved
            if case["expected_document"] not in actual_filenames and case["expected_document"] != "test_doc.txt":
                # We won't strictly fail on document right now, just note it in reasoning
                reasoning += f" | NOTE: Expected doc {case['expected_document']} not cited. Cited: {actual_filenames}"
            
            if passed:
                passed_count += 1
                print(f"✅ PASSED in {duration:.2f}s: {reasoning}")
            else:
                print(f"❌ FAILED in {duration:.2f}s: {reasoning}")
                
            # Write row to CSV
            writer.writerow([
                case['id'], 
                case['question'], 
                ", ".join(case['expected_facts']), 
                case['expected_document'], 
                generated_answer.replace('\n', ' '), 
                "YES" if passed else "NO", 
                reasoning, 
                ", ".join(actual_filenames)
            ])
            
    # Calculate and report final accuracy
    total = len(GOLDEN_TEST_CASES)
    accuracy = (passed_count / total) * 100
    
    print("\n" + "="*80)
    print(f"📊 FINAL PERTINENCE ACCURACY: {accuracy}% ({passed_count}/{total} passed)")
    print(f"📄 CSV Report generated at: {csv_path}")
    print("="*80 + "\n")
    
    # Assert that we have at least 50% accuracy for the CI to pass (can be increased later)
    assert accuracy >= 50, f"Accuracy too low: {accuracy}%"
