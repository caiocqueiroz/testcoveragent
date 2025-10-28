from django.test import RequestFactory, TestCase

from apps.corecode.middleware import SiteWideConfigs
from apps.corecode.models import AcademicSession, AcademicTerm


class SiteWideConfigsMiddlewareTest(TestCase):
    def setUp(self):
        """Set up test fixtures"""
        self.factory = RequestFactory()
        self.get_response = lambda request: None
        self.middleware = SiteWideConfigs(self.get_response)

    def test_middleware_sets_current_session_on_request(self):
        """Verifica se o middleware adiciona current_session ao request"""
        session = AcademicSession.objects.create(name="2024/2025", current=True)
        request = self.factory.get("/")

        self.middleware(request)

        self.assertTrue(hasattr(request, "current_session"))
        self.assertEqual(request.current_session, session)
        self.assertEqual(request.current_session.name, "2024/2025")

    def test_middleware_sets_current_term_on_request(self):
        """Verifica se o middleware adiciona current_term ao request"""
        AcademicSession.objects.create(name="2024/2025", current=True)
        term = AcademicTerm.objects.create(name="First Term", current=True)
        request = self.factory.get("/")

        self.middleware(request)

        self.assertTrue(hasattr(request, "current_term"))
        self.assertEqual(request.current_term, term)
        self.assertEqual(request.current_term.name, "First Term")

    def test_middleware_sets_both_session_and_term(self):
        """Verifica se o middleware adiciona ambos session e term ao request"""
        session = AcademicSession.objects.create(name="2024/2025", current=True)
        term = AcademicTerm.objects.create(name="First Term", current=True)
        request = self.factory.get("/")

        self.middleware(request)

        self.assertTrue(hasattr(request, "current_session"))
        self.assertTrue(hasattr(request, "current_term"))
        self.assertEqual(request.current_session, session)
        self.assertEqual(request.current_term, term)

    def test_middleware_handles_missing_current_session(self):
        """Verifica comportamento quando não há sessão atual definida"""
        # Make sure no current session exists
        AcademicSession.objects.filter(current=True).delete()
        # Create a term but no session marked as current
        AcademicTerm.objects.create(name="First Term", current=True)
        request = self.factory.get("/")

        # Should raise DoesNotExist exception
        with self.assertRaises(AcademicSession.DoesNotExist):
            self.middleware(request)

    def test_middleware_handles_missing_current_term(self):
        """Verifica comportamento quando não há termo atual definido"""
        # Make sure no current term exists
        AcademicTerm.objects.filter(current=True).delete()
        # Create a session but no term marked as current
        AcademicSession.objects.create(name="2024/2025", current=True)
        request = self.factory.get("/")

        # Should raise DoesNotExist exception
        with self.assertRaises(AcademicTerm.DoesNotExist):
            self.middleware(request)
