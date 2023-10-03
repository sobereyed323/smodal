from django.test import TestCase
from django.core.exceptions import ValidationError
from Smodal.social_media_bot import SocialMediaBot
from Smodal.sale_items import SaleItem, ChatBot
import uuid
import os
from .models import OIDCConfiguration
import json

class SmodalTest(TestCase):
    def setUp(self):
        self.bot = SocialMediaBot()
        self.sale_item = SaleItem()
        self.chat_bot = ChatBot()
        self.pactflow_data = OIDCConfiguration.objects.first()
        self.expected_headers = json.loads(self.pactflow_data.pactflow_response_headers)
        self.expected_body = json.loads(self.pactflow_data.pactflow_response_body)

        # Adjusting for Replit environment
        if 'REPLIT' in os.environ:
            self.bot.base_url = os.getenv('REPLIT_DB_URL')
            self.sale_item.base_url = os.getenv('REPLIT_DB_URL')
            self.chat_bot.base_url = os.getenv('REPLIT_DB_URL')

    # existing test cases here...

    def test_pactflow_response_headers_saved_correctly(self):
        self.assertEqual(str(self.pactflow_data.pactflow_response_headers), str(self.expected_headers))

    def test_pactflow_response_body_saved_correctly(self):
        self.assertEqual(str(self.pactflow_data.pactflow_response_body), str(self.expected_body))
