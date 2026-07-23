import os
from notion_client import Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

NOTION_TOKEN = os.getenv("NOTION_TOKEN")
DATABASE_ID = os.getenv("DATABASE_ID")

print(f"Loaded Token: {NOTION_TOKEN[:10]}..." if NOTION_TOKEN else "NOTION_TOKEN is missing!")
print(f"Loaded Database ID: {DATABASE_ID}" if DATABASE_ID else "DATABASE_ID is missing!")

try:
    notion = Client(auth=NOTION_TOKEN)
    print("\nAttempting to query Notion database...")
    
    # Query the Notion database using the data sources method
    response = notion.data_sources.query(data_source_id=DATABASE_ID)
    results = response.get("results", [])
    print(f"Success! Retrieved {len(results)} rows from Notion.")
    
    scores = []
    for page in results:
        props = page.get("properties", {})
        
        # Look for a score property across common naming conventions
        score_val = None
        for key in ["Score", "score", "Sentiment", "sentiment", "Value", "value"]:
            if key in props:
                prop_data = props[key]
                prop_type = prop_data.get("type")
                
                if prop_type == "number":
                    score_val = prop_data.get("number")
                elif prop_type == "formula":
                    formula_data = prop_data.get("formula", {})
                    if formula_data.get("type") == "number":
                        score_val = formula_data.get("number")
                elif prop_type == "rollup":
                    rollup_data = prop_data.get("rollup", {})
                    if rollup_data.get("type") == "number":
                        score_val = rollup_data.get("number")
                break
        
        if score_val is not None:
            scores.append(float(score_val))

    print(f"Extracted valid scores: {scores}")
    
    if scores:
        avg_score = sum(scores) / len(scores)
        print(f"Calculated Average Score: {round(avg_score, 2)}")
    else:
        print("Warning: No valid numeric scores found in the rows.")

except Exception as e:
    print(f"\n[ERROR CAUGHT]: {e}")