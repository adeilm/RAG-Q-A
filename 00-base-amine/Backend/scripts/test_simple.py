import httpx
import json
import time

API_URL = "http://localhost:8000/query"

def run_test(query: str):
    payload = {
        "query": query,
        "session_id": "global",
        "conversation_history": [],
        "preferred_provider": "groq"
    }
    
    with open("test_output.txt", "a", encoding="utf-8") as f:
        f.write(f"\n{'='*50}\nRUNNING QUERY: {query}\n{'='*50}\n")
        
    try:
        response = httpx.post(API_URL, json=payload, timeout=240.0)
        data = response.json()
        
        with open("test_output.txt", "a", encoding="utf-8") as f:
            if 'route_log' in data:
                for log in data['route_log']:
                    if 'node' in log and log['node'] == 'classify_intent':
                        intent_data = log.get('data', {}).get('intent', {})
                        sql_filters = intent_data.get('sql_filters', {})
                        f.write(f"EXTRACTED SQL FILTERS: {sql_filters}\n")
            
            f.write(f"ANSWER:\n{data.get('answer', 'No answer')}\n")
            
            sources = data.get("sources", [])
            f.write(f"SOURCES USED ({len(sources)}):\n")
            for i, src in enumerate(sources):
                f.write(f"  {i+1}. {src.get('metadata', {}).get('filename', 'Unknown')} (Project: {src.get('metadata', {}).get('project_name', 'Unknown')})\n")
    except Exception as e:
        with open("test_output.txt", "a", encoding="utf-8") as f:
            f.write(f"FAILED: {str(e)}\n")

if __name__ == "__main__":
    with open("test_output.txt", "w", encoding="utf-8") as f:
        f.write("STARTING TESTS...\n")
    
    print("Testing strict locking...")
    run_test("Search ONLY in Project Tunis-A45. What is the wind load or zone vent for this specific project?")
    
    time.sleep(2)
    
    print("Testing precedent finder...")
    run_test("Find me projects that are similar to a mât braconné of 30m height. I want to use one as a precedent.")
    
    print("Tests finished. Results are in test_output.txt")
