"""
Example: How to integrate BI Platform API Engine in a Flask project.
"""
from flask import Flask, request, jsonify, send_file
from pathlib import Path
import os

from api_engine.core.standardized_interface import StandardizedAPIEngine

app = Flask(__name__)

# Initialize API Engine
api_engine = StandardizedAPIEngine()


@app.route('/api/send-email', methods=['POST'])
def send_email():
    """
    Flask route to send email.
    
    POST /api/send-email
    {
        "to": "user@example.com",
        "subject": "Hello",
        "content": "Message"
    }
    """
    data = request.get_json()
    
    result = api_engine.send_email({
        "to": data.get("to"),
        "subject": data.get("subject"),
        "content": data.get("content")
    })
    
    return jsonify(result), 200 if result.get("status") == "success" else 500


@app.route('/api/upload-file', methods=['POST'])
def upload_file():
    """
    Flask route to upload file.
    
    POST /api/upload-file
    Form data: file, bucket
    """
    if 'file' not in request.files:
        return jsonify({"status": "error", "error": "No file provided"}), 400
    
    file = request.files['file']
    bucket = request.form.get('bucket', 'documents')
    
    # Save temporarily
    temp_path = Path(f"/tmp/{file.filename}")
    file.save(str(temp_path))
    
    try:
        result = api_engine.upload_file(temp_path, {
            "bucket": bucket,
            "object_name": file.filename
        })
        
        # Clean up
        temp_path.unlink()
        
        return jsonify(result)
    except Exception as e:
        return jsonify({"status": "error", "error": str(e)}), 500


@app.route('/api/create-envelope', methods=['POST'])
def create_envelope():
    """
    Flask route to create e-signature envelope.
    
    POST /api/create-envelope
    Form data: document, signers (JSON)
    """
    if 'document' not in request.files:
        return jsonify({"status": "error", "error": "No document provided"}), 400
    
    document = request.files['document']
    signers = request.form.get('signers', '[]')
    
    import json
    signers_list = json.loads(signers)
    
    # Save temporarily
    temp_path = Path(f"/tmp/{document.filename}")
    document.save(str(temp_path))
    
    try:
        result = api_engine.create_envelope(temp_path, {
            "signers": signers_list,
            "subject": request.form.get('subject')
        })
        
        # Clean up
        temp_path.unlink()
        
        return jsonify(result)
    except Exception as e:
        return jsonify({"status": "error", "error": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True, port=5000)

