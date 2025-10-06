import requests
import json
import time

# Submit query
print("Submitting query...")
response = requests.post(
    "http://localhost:9000/api/query",
    json={"query": "Show all employees in Engineering"}
)

result = response.json()
print("\n=== QUERY RESPONSE ===")
print(json.dumps(result, indent=2))

# Get query log ID
query_log_id = result.get("query_log_id")
if not query_log_id:
    print("\nNo query_log_id in response!")
    exit(1)

print(f"\nQuery Log ID: {query_log_id}")
print(f"Evaluation Status: {result.get('evaluation_status')}")

# Poll for RAGAS scores
print("\nWaiting for RAGAS evaluation...")
for i in range(15):  # Wait up to 30 seconds
    time.sleep(2)
    status_response = requests.get(f"http://localhost:9000/api/query/{query_log_id}")
    status_data = status_response.json()

    eval_status = status_data.get("evaluation_status")
    print(f"  [{i*2}s] Status: {eval_status}")

    if eval_status == "completed":
        print("\n=== RAGAS SCORES ===")
        print(json.dumps(status_data.get("ragas_scores"), indent=2))
        break
    elif eval_status == "failed":
        print("\n[X] RAGAS evaluation failed!")
        break
else:
    print("\n[!] Timeout waiting for RAGAS evaluation")
