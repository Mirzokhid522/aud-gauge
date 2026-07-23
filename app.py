import os
from flask import Flask, jsonify, render_template
from notion_client import Client
from dotenv import load_dotenv

# Load environment variables
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
            
            # Look for a score property (adjust column name if yours differs, e.g., 'Score' or 'Sentiment')
            # Checking multiple potential column naming conventions safely
            score_val = None
            for key in ["Score", "score", "Sentiment", "sentiment", "Value", "value"]:
                if key in props:
                    prop_data = props[key]
                    prop_type = prop_data.get("type")
                    
                    if prop_type == "number":
                        score_val = prop_data.get("number")
                    elif prop_type == "formula":
                        formula_data = prop_data.get("formula", {})
                        f_type = formula_data.get("type")
                        if f_type == "number":
                            score_val = formula_data.get("number")
                    elif prop_type == "rollup":
                        rollup_data = prop_data.get("rollup", {})
                        r_type = rollup_data.get("type")
                        if r_type == "number":
                            score_val = rollup_data.get("number")
                    break
            
            if score_val is not None:
                scores.append(float(score_val))

        # Calculate average score or default to neutral (50) if empty
        if scores:
            avg_score = sum(scores) / len(scores)
        else:
            avg_score = 50.0

        # Categorize sentiment based on score range (0 to 100 scale)
        if avg_score >= 80:
            sentiment = "Very Bullish"
        elif avg_score >= 60:
            sentiment = "Bullish"
        elif avg_score >= 40:
            sentiment = "Neutral"
        elif avg_score >= 20:
            sentiment = "Bearish"
        else:
            sentiment = "Very Bearish"

        return jsonify({
            "score": round(avg_score, 2),
            "sentiment": sentiment,
            "total_rows": len(results)
        })

    except Exception as e:
        print(f"Error fetching Notion data: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, port=5000)