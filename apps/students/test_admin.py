from django.test import TestCase


class StudentsAdminTest(TestCase):
    def test_admin_module_can_be_imported(self):
        """Testa se módulo admin pode ser importado e acessado sem erros"""
        try:
            import apps.students.admin as admin_module

            self.assertIsNotNone(admin_module)
        except ImportError as e:
            self.fail(f"Failed to import admin module: {e}")
