import asyncio
import httpx
import json
from pprint import pprint

API_URL = "http://localhost:8000/query"

async def test_query(test_name: str, query: str):
    print(f"\n{'='*50}\n🚀 RUNNING TEST: {test_name}\n{'='*50}")
    print(f"Query: \"{query}\"")
    
    payload = {
        "query": query,
        "session_id": "global",
        "conversation_history": [],
        "preferred_provider": "groq"
    }
    
    # Long timeout: reranker over a large global corpus can take several minutes
    async with httpx.AsyncClient(timeout=600.0) as client:
        try:
            response = await client.post(API_URL, json=payload)
            response.raise_for_status()
            data = response.json()
            
            print(f"\n✅ ROUTE CHOSEN: {data.get('route')}")
            
            # Print the sql_filters if any were extracted
            if 'route_log' in data:
                for log in data['route_log']:
                    if 'node' in log and log['node'] == 'classify_intent':
                        intent_data = log.get('data', {}).get('intent', {})
                        sql_filters = intent_data.get('sql_filters', {})
                        print(f"📊 EXTRACTED SQL FILTERS: {sql_filters}")
            
            print(f"\n🤖 ANSWER:")
            print("-" * 40)
            print(data.get("answer", "No answer provided."))
            print("-" * 40)
            
            sources = data.get("sources", [])
            print(f"\n📚 SOURCES USED ({len(sources)}):")
            for i, src in enumerate(sources):
                print(f"  {i+1}. {src.get('metadata', {}).get('filename', 'Unknown')} (Project: {src.get('metadata', {}).get('project_name', 'Unknown')})")
                
        except Exception as e:
            print(f"\n❌ FAILED: {str(e)}")
            if hasattr(e, 'response') and e.response:
                print(e.response.text)

async def main():
    # 1. Test Strict Project Locking
    await test_query(
        "Strict Project Locking",
        "Search ONLY in Project Tunis-A45. What is the wind load or zone vent for this specific project?"
    )
    
    # 2. Test Precedent Finder (Hybrid Search by parameters)
    await test_query(
        "Precedent Finder (Hybrid Search)",
        "Find me projects that are similar to a mât braconné of 30m height. I want to use one as a precedent."
    )

if __name__ == "__main__":
    asyncio.run(main())
