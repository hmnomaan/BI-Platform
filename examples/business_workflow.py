"""
Example business workflow using the API Engine.
This demonstrates a complete contract signing workflow.
"""
from pathlib import Path
from api_engine.core.api_engine import APIEngine
from api_engine.utils.logging import setup_logging

# Setup logging
setup_logging(log_level="INFO", log_file=Path("logs/workflow.log"))

# Initialize API Engine
engine = APIEngine()

def contract_signing_workflow(contract_path: Path, signers: list):
    """
    Complete contract signing workflow:
    1. Upload document to storage
    2. Create e-signature envelope
    3. Send notification email
    4. Log everything
    """
    logger = setup_logging().bind(name="Workflow")
    
    try:
        # Step 1: Upload document to storage
        logger.info("Step 1: Uploading contract to storage...")
        storage_url = engine.upload_file(contract_path, bucket="contracts")
        logger.info(f"Contract uploaded: {storage_url}")
        
        # Step 2: Create e-signature envelope
        logger.info("Step 2: Creating e-signature envelope...")
        envelope_id = engine.create_envelope(
            document=contract_path,
            signers=signers,
            subject="Contract for Signature"
        )
        logger.info(f"Envelope created: {envelope_id}")
        
        # Step 3: Send notification email to first signer
        logger.info("Step 3: Sending notification email...")
        first_signer = signers[0]
        email_result = engine.send_email(
            to=first_signer['email'],
            subject="Contract for Signature",
            content=f"""
            <h2>Contract Signing Request</h2>
            <p>Hello {first_signer.get('name', 'there')},</p>
            <p>You have been requested to sign a contract. Please review and sign at your earliest convenience.</p>
            <p>Envelope ID: {envelope_id}</p>
            <p>Thank you!</p>
            """
        )
        logger.info(f"Email sent: {email_result.get('message_id')}")
        
        # Step 4: Log completion
        logger.info(f"Contract workflow completed successfully: {envelope_id}")
        
        return {
            "status": "success",
            "envelope_id": envelope_id,
            "storage_url": storage_url,
            "email_sent": True
        }
        
    except Exception as e:
        logger.error(f"Workflow failed: {e}")
        return {
            "status": "error",
            "error": str(e)
        }


# Example usage
if __name__ == "__main__":
    # Define contract and signers
    contract = Path("contracts/sample_contract.pdf")
    signers = [
        {"email": "john.doe@example.com", "name": "John Doe", "role": "Client"},
        {"email": "jane.smith@example.com", "name": "Jane Smith", "role": "Vendor"}
    ]
    
    # Run workflow
    result = contract_signing_workflow(contract, signers)
    print(f"Workflow result: {result}")
