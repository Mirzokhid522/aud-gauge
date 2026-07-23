import os
from flask import Flask, jsonify, render_template
from notion_client import Client
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

NOTION_TOKEN = os.getenv("NOTION_TOKEN")
DATABASE_ID = os.getenv("DATABASE_ID")

notion = Client(auth=NOTION_TOKEN)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/score", methods=["GET"])
def get_market_score():
    try:
        # Query the Notion database using the data sources method
        response = notion.data_sources.query(data_source_id=DATABASE_ID)
        results = response.get("results", [])
        
        scores = []
        for page in results:
            props = page.get("properties", {})
            
            score_val = None
            # Check standard naming conventions for your score/sentiment column
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

        if scores:
            avg_score = sum(scores) / len(scores)
        else:
            avg_score = 0.0

        return jsonify({
            "score": round(avg_score, 4),
            "total_rows": len(results)
        })

    except Exception as e:
        print(f"Error fetching Notion data: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, port=5000)