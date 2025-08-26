from flask import Flask, render_template, jsonify

# Initialize the Flask application
app = Flask(__name__, template_folder='.')

# --- Routes ---

@app.route('/')
def dashboard():
    """
    Renders the main dashboard page.
    The HTML file itself contains static data for the UI,
    but this endpoint could be expanded to pass dynamic data.
    """
    return render_template('app.html')

@app.route('/api/data')
def get_data():
    """
    API endpoint to provide data to the charts.
    This allows the frontend to dynamically fetch new data without reloading the page.
    In a real application, this function would query a database or a data processing pipeline.
    """
    sentiment_data = {
        'labels': ['Negative', 'Neutral', 'Positive'],
        'values': [65, 25, 10]
    }
    
    topic_data = {
        'labels': ['#BoycottIndia', 'Kashmir Conflict', 'Economic "Failure"', 'Human Rights', 'Fake News'],
        'values': [1200, 950, 700, 550, 400]
    }

    return jsonify({
        'sentiment': sentiment_data,
        'topics': topic_data
    })

# --- Main Execution ---

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
