from django.http import HttpResponse
from django.test import RequestFactory, TestCase

from apps.corecode.middleware import SiteWideConfigs
from apps.corecode.models import AcademicSession, AcademicTerm


class SiteWideConfigsMiddlewareTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.session = AcademicSession.objects.create(name="2023/2024", current=True)
        self.term = AcademicTerm.objects.create(name="First Term", current=True)

        def dummy_view(request):
            return HttpResponse("OK")

        self.middleware = SiteWideConfigs(dummy_view)

    def test_middleware_adds_current_session_to_request(self):
        """Testa se middleware adiciona sessão atual ao request"""
        request = self.factory.get("/")
        response = self.middleware(request)

        self.assertEqual(request.current_session.name, "2023/2024")
        self.assertTrue(request.current_session.current)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode(), "OK")

    def test_middleware_adds_current_term_to_request(self):
        """Testa se middleware adiciona termo atual ao request"""
        request = self.factory.get("/")
        response = self.middleware(request)

        self.assertEqual(request.current_term.name, "First Term")
        self.assertTrue(request.current_term.current)

    def test_middleware_handles_missing_current_session(self):
        """Testa erro quando não há sessão ativa"""
        AcademicSession.objects.all().update(current=False)
        request = self.factory.get("/")

        with self.assertRaises(AcademicSession.DoesNotExist):
            self.middleware(request)

    def test_middleware_handles_missing_current_term(self):
        """Testa erro quando não há termo ativo"""
        AcademicTerm.objects.all().update(current=False)
        request = self.factory.get("/")

        with self.assertRaises(AcademicTerm.DoesNotExist):
            self.middleware(request)

    def test_middleware_with_multiple_sessions_picks_current(self):
        """Testa que middleware escolhe a sessão marcada como current"""
        AcademicSession.objects.create(name="2022/2023", current=False)
        AcademicSession.objects.create(name="2024/2025", current=False)

        request = self.factory.get("/")
        response = self.middleware(request)

        # Deve pegar apenas a sessão atual (2023/2024)
        self.assertEqual(request.current_session.name, "2023/2024")
        self.assertTrue(request.current_session.current)

    def test_middleware_with_multiple_terms_picks_current(self):
        """Testa que middleware escolhe o termo marcado como current"""
        AcademicTerm.objects.create(name="Second Term", current=False)
        AcademicTerm.objects.create(name="Third Term", current=False)

        request = self.factory.get("/")
        response = self.middleware(request)

        # Deve pegar apenas o termo atual (First Term)
        self.assertEqual(request.current_term.name, "First Term")
        self.assertTrue(request.current_term.current)
