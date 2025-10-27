from django.test import TestCase


class ResultAdminTest(TestCase):
    def test_admin_module_can_be_imported(self):
        """Testa se módulo admin pode ser importado sem erros"""
        try:
            from apps.result import admin  # noqa: F401

            self.assertTrue(True)
        except ImportError as e:
            self.fail(f"Failed to import admin module: {e}")

    def test_admin_module_exists(self):
        """Testa se arquivo admin.py existe e está acessível"""
        import apps.result.admin as admin_module

        self.assertIsNotNone(admin_module)
