"""
Example usage of the API Engine.
"""
from pathlib import Path
from api_engine.core.api_engine import APIEngine
from api_engine.utils.logging import setup_logging

# Setup logging
setup_logging(log_level="INFO")

# Initialize API Engine
engine = APIEngine()

# Example 1: Send an email
try:
    result = engine.send_email(
        to="recipient@example.com",
        subject="Test Email",
        content="<h1>Hello from BI Platform!</h1><p>This is a test email.</p>"
    )
    print(f"Email sent: {result}")
except Exception as e:
    print(f"Email sending failed: {e}")

# Example 2: Upload a file to storage
try:
    file_path = Path("example_document.pdf")
    if file_path.exists():
        url = engine.upload_file(file_path, bucket="documents")
        print(f"File uploaded: {url}")
except Exception as e:
    print(f"File upload failed: {e}")

# Example 3: Create an e-signature envelope
try:
    document = Path("contract.pdf")
    if document.exists():
        signers = [
            {"email": "signer1@example.com", "name": "John Doe"},
            {"email": "signer2@example.com", "name": "Jane Smith"}
        ]
        envelope_id = engine.create_envelope(document, signers)
        print(f"Envelope created: {envelope_id}")
except Exception as e:
    print(f"Envelope creation failed: {e}")

# Example 4: Search
try:
    results = engine.search("business intelligence", index="documents", limit=5)
    print(f"Search returned {len(results)} results")
except Exception as e:
    print(f"Search failed: {e}")

# Example 5: Send physical mail
try:
    to_address = {
        "name": "John Doe",
        "address_line1": "123 Main St",
        "city": "New York",
        "state": "NY",
        "zip": "10001",
        "country": "US"
    }
    from_address = {
        "name": "BI Platform",
        "address_line1": "456 Business Ave",
        "city": "San Francisco",
        "state": "CA",
        "zip": "94102",
        "country": "US"
    }
    letter_id = engine.send_letter(
        to_address=to_address,
        from_address=from_address,
        content="<h1>Important Document</h1><p>Please review this document.</p>"
    )
    print(f"Letter sent: {letter_id}")
except Exception as e:
    print(f"Letter sending failed: {e}")

