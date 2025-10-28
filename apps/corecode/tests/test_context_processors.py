from django.test import RequestFactory, TestCase

from apps.corecode.context_processors import site_defaults
from apps.corecode.models import AcademicSession, AcademicTerm, SiteConfig


class SiteDefaultsContextProcessorTest(TestCase):
    def setUp(self):
        """Set up test fixtures"""
        self.factory = RequestFactory()
        # Create current session and term
        self.session = AcademicSession.objects.create(
            name="2024/2025", current=True
        )
        self.term = AcademicTerm.objects.create(name="First Term", current=True)

    def test_site_defaults_returns_current_session_and_term(self):
        """Verifica se o context processor retorna sessão e termo atuais"""
        request = self.factory.get("/")
        context = site_defaults(request)

        self.assertIn("current_session", context)
        self.assertIn("current_term", context)
        self.assertEqual(context["current_session"], "2024/2025")
        self.assertEqual(context["current_term"], "First Term")

    def test_site_defaults_with_multiple_site_configs(self):
        """Verifica se todas as configurações do site são incluídas no contexto"""
        # Create multiple site configurations
        SiteConfig.objects.create(key="school_name", value="Test School")
        SiteConfig.objects.create(key="school_motto", value="Excellence in Education")
        SiteConfig.objects.create(key="school_address", value="123 Test Street")

        request = self.factory.get("/")
        context = site_defaults(request)

        # Check that all site configs are in the context
        self.assertIn("school_name", context)
        self.assertIn("school_motto", context)
        self.assertIn("school_address", context)
        self.assertEqual(context["school_name"], "Test School")
        self.assertEqual(context["school_motto"], "Excellence in Education")
        self.assertEqual(context["school_address"], "123 Test Street")

    def test_site_defaults_with_no_site_configs(self):
        """Verifica comportamento quando não há configurações de site"""
        # Make sure no site configs exist
        SiteConfig.objects.all().delete()
        
        request = self.factory.get("/")
        context = site_defaults(request)

        # Should still have session and term
        self.assertIn("current_session", context)
        self.assertIn("current_term", context)
        # Should have exactly 2 keys (session and term) when no site configs exist
        self.assertEqual(len(context), 2)
