"""
Example: How to integrate BI Platform API Engine in a Django project.

This example shows how to use the API Engine in Django views and models.
"""
# Django settings.py - Add to INSTALLED_APPS (if creating a Django app)
# INSTALLED_APPS = [
#     ...
#     'api_engine',  # If packaged as Django app
# ]

# Django views.py example
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
from pathlib import Path

from api_engine.core.standardized_interface import StandardizedAPIEngine

# Initialize API Engine (can be done in Django settings or as singleton)
api_engine = StandardizedAPIEngine()


@csrf_exempt
@require_http_methods(["POST"])
def send_notification_email(request):
    """
    Django view to send email via API Engine.
    
    POST /api/send-email/
    {
        "to": "user@example.com",
        "subject": "Notification",
        "content": "Hello!"
    }
    """
    try:
        data = json.loads(request.body)
        
        result = api_engine.send_email({
            "to": data.get("to"),
            "subject": data.get("subject"),
            "content": data.get("content"),
            "from_email": "noreply@yourcompany.com"
        })
        
        if result.get("status") == "success":
            return JsonResponse(result, status=200)
        else:
            return JsonResponse(result, status=500)
    
    except Exception as e:
        return JsonResponse({"status": "error", "error": str(e)}, status=400)


@csrf_exempt
@require_http_methods(["POST"])
def upload_document(request):
    """
    Django view to upload document to cloud storage.
    
    POST /api/upload-document/
    Form data: file, bucket
    """
    try:
        uploaded_file = request.FILES.get('file')
        bucket = request.POST.get('bucket', 'documents')
        
        # Save uploaded file temporarily
        temp_path = Path(f"/tmp/{uploaded_file.name}")
        with open(temp_path, 'wb+') as destination:
            for chunk in uploaded_file.chunks():
                destination.write(chunk)
        
        # Upload to storage
        result = api_engine.upload_file(temp_path, {
            "bucket": bucket,
            "object_name": uploaded_file.name
        })
        
        # Clean up temp file
        temp_path.unlink()
        
        return JsonResponse(result)
    
    except Exception as e:
        return JsonResponse({"status": "error", "error": str(e)}, status=500)


# Django models.py example - Using in a model method
from django.db import models

class Contract(models.Model):
    """Example Django model using API Engine."""
    title = models.CharField(max_length=200)
    document_path = models.FileField(upload_to='contracts/')
    status = models.CharField(max_length=20, default='draft')
    
    def send_for_signature(self, signers):
        """Send contract for e-signature."""
        result = api_engine.create_envelope(
            Path(self.document_path.path),
            {
                "signers": signers,
                "subject": f"Contract: {self.title}"
            }
        )
        
        if result.get("status") == "success":
            self.status = "pending_signature"
            self.save()
        
        return result


# Django management command example
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = 'Send weekly report emails'
    
    def handle(self, *args, **options):
        """Send weekly reports using API Engine."""
        from myapp.models import User
        
        users = User.objects.filter(subscribed_to_reports=True)
        
        for user in users:
            result = api_engine.send_email({
                "to": user.email,
                "subject": "Weekly Report",
                "content": f"<h1>Weekly Report for {user.name}</h1>..."
            })
            
            if result.get("status") == "success":
                self.stdout.write(f"Sent report to {user.email}")
            else:
                self.stderr.write(f"Failed to send to {user.email}: {result.get('error')}")

