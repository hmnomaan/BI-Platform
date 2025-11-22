# tests/test_bi_dashboard.py
class TestBIPlatform:
    def test_data_loading_performance(self):
        """Test loading 1M records within 3 seconds"""
        start_time = time.time()
        df = data_manager.load_large_dataset()
        load_time = time.time() - start_time
        assert load_time <= 3.0
    
    def test_chart_interactivity(self):
        """Test chart linking functionality"""
        dashboard = create_test_dashboard()
        assert dashboard.has_interactive_features()

# tests/test_api_engine.py  
class TestAPIEngine:
    def test_provider_switching(self):
        """Test switching email providers with minimal code changes"""
        email_service = EmailService(provider='sendgrid')
        # Switch to mailgun
        email_service.switch_provider('mailgun')
        assert email_service.current_provider == 'mailgun'