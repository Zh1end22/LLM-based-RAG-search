from flask import Flask, request, jsonify
import os
from utils import search_articles, process_articles

app = Flask(__name__)

@app.route('/query', methods=['POST'])
def query():
    """
    Handles the POST request to '/query'. Extracts the query from the request,
    processes it through the search and process functions,
    and returns the generated answer.
    """
    data = request.get_json()
    query_text = data.get("query", "")

    if not query_text:
        return jsonify({"error": "Query is required"}), 400

    try:
        # Step 1: Search for articles based on the query
        articles = search_articles(query_text)
        if not articles:
            return jsonify({"error": "No articles found"}), 404

        # Step 2: Process articles (scrape content and generate answer)
        answer = process_articles(articles, query_text)

        # Return the generated answer as JSON response
        return jsonify({"answer": answer})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='localhost', port=5001)