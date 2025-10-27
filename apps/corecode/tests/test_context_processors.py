from django.test import RequestFactory, TestCase

from apps.corecode.context_processors import site_defaults
from apps.corecode.models import AcademicSession, AcademicTerm, SiteConfig


class ContextProcessorsTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.session = AcademicSession.objects.create(name="2023/2024", current=True)
        self.term = AcademicTerm.objects.create(name="First Term", current=True)
        SiteConfig.objects.create(key="school_name", value="Test School")
        SiteConfig.objects.create(key="school_slogan", value="Excellence in Education")

    def test_site_defaults_returns_correct_context(self):
        """Testa se context_processor retorna sessão e termo corretos"""
        request = self.factory.get("/")
        context = site_defaults(request)

        self.assertEqual(context["current_session"], "2023/2024")
        self.assertEqual(context["current_term"], "First Term")
        self.assertEqual(context["school_name"], "Test School")
        self.assertEqual(context["school_slogan"], "Excellence in Education")

    def test_site_defaults_with_no_current_session(self):
        """Testa comportamento quando não há sessão ativa"""
        AcademicSession.objects.all().update(current=False)
        request = self.factory.get("/")

        with self.assertRaises(AcademicSession.DoesNotExist):
            site_defaults(request)

    def test_site_defaults_with_no_current_term(self):
        """Testa comportamento quando não há termo ativo"""
        AcademicTerm.objects.all().update(current=False)
        request = self.factory.get("/")

        with self.assertRaises(AcademicTerm.DoesNotExist):
            site_defaults(request)

    def test_site_defaults_with_multiple_configs(self):
        """Testa com múltiplas configurações do site"""
        SiteConfig.objects.create(key="address", value="123 Main St")
        SiteConfig.objects.create(key="phone", value="555-1234")

        request = self.factory.get("/")
        context = site_defaults(request)

        self.assertEqual(context["address"], "123 Main St")
        self.assertEqual(context["phone"], "555-1234")
        # Verifica que as configs anteriores ainda estão presentes
        self.assertEqual(context["school_name"], "Test School")

    def test_site_defaults_with_no_configs(self):
        """Testa quando não há configurações de site"""
        SiteConfig.objects.all().delete()

        request = self.factory.get("/")
        context = site_defaults(request)

        # Ainda deve retornar sessão e termo
        self.assertEqual(context["current_session"], "2023/2024")
        self.assertEqual(context["current_term"], "First Term")
        # Mas não deve ter configs extras
        self.assertNotIn("school_name", context)
