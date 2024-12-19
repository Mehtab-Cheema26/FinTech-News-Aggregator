import subprocess

from flask import Flask, jsonify, send_file
import pandas as pd

app = Flask(__name__)

@app.route('/data', methods=['GET'])
def get_data():
    # Run the reddit_post.py script
    subprocess.run(['python', 'reddit_post.py'], check = True)

    # Read the CSV file
    df = pd.read_csv('../../Reddit/reddit_python.csv')
    # Convert to a list of dictionaries
    data = df.to_dict(orient='records')
    return jsonify(data)

if __name__ == '__main__':
    app.run(debug=True)
