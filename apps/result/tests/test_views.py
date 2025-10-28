from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse

from apps.corecode.models import (
    AcademicSession,
    AcademicTerm,
    StudentClass,
    Subject,
)
from apps.result.models import Result
from apps.students.models import Student


class CreateResultViewTest(TestCase):
    def setUp(self):
        """Set up test fixtures"""
        self.client = Client()
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.client.login(username="testuser", password="testpass")

        # Create academic session and term
        self.session = AcademicSession.objects.create(
            name="2024/2025", current=True
        )
        self.term = AcademicTerm.objects.create(name="First Term", current=True)

        # Create subjects
        self.subject1, _ = Subject.objects.get_or_create(name="Mathematics")
        self.subject2, _ = Subject.objects.get_or_create(name="English")

        # Create class
        self.student_class, _ = StudentClass.objects.get_or_create(name="Grade 10")

        # Create students
        self.student1 = Student.objects.create(
            registration_number="STU001",
            surname="Doe",
            firstname="John",
            current_class=self.student_class,
        )
        self.student2 = Student.objects.create(
            registration_number="STU002",
            surname="Smith",
            firstname="Jane",
            current_class=self.student_class,
        )
        self.student3 = Student.objects.create(
            registration_number="STU003",
            surname="Brown",
            firstname="Bob",
            current_class=None,  # No class assigned
        )

    def test_create_result_GET_shows_student_list(self):
        """Verifica se a view de criação exibe lista de estudantes"""
        url = reverse("create-result")
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "result/create_result.html")
        self.assertIn("students", response.context)
        # Should show all students
        self.assertEqual(response.context["students"].count(), 3)

    def test_create_result_POST_step1_selects_students(self):
        """Verifica primeiro passo: seleção de estudantes"""
        url = reverse("create-result")
        response = self.client.post(
            url, {"students": [str(self.student1.id), str(self.student2.id)]}
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "result/create_result_page2.html")
        self.assertIn("form", response.context)
        self.assertIn("students", response.context)
        self.assertEqual(response.context["count"], 2)

    def test_create_result_POST_no_students_selected_shows_warning(self):
        """Verifica aviso quando nenhum estudante é selecionado"""
        url = reverse("create-result")
        response = self.client.post(url, {})

        self.assertEqual(response.status_code, 200)
        messages = list(response.context["messages"])
        self.assertEqual(len(messages), 1)
        self.assertIn("didnt select any student", str(messages[0]))

    def test_create_result_POST_creates_results_for_multiple_students(self):
        """Verifica criação em massa de resultados"""
        url = reverse("create-result")
        student_ids = f"{self.student1.id},{self.student2.id}"

        response = self.client.post(
            url,
            {
                "finish": "true",
                "session": self.session.id,
                "term": self.term.id,
                "subjects": [self.subject1.id, self.subject2.id],
                "students": student_ids,
            },
        )

        # Should redirect to edit-results
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("edit-results"))

        # Check that results were created
        results = Result.objects.all()
        # 2 students × 2 subjects = 4 results
        self.assertEqual(results.count(), 4)

        # Verify results for student1
        student1_results = Result.objects.filter(student=self.student1)
        self.assertEqual(student1_results.count(), 2)

        # Verify results for student2
        student2_results = Result.objects.filter(student=self.student2)
        self.assertEqual(student2_results.count(), 2)

    def test_create_result_prevents_duplicate_results(self):
        """Verifica se não cria resultados duplicados"""
        # Create an existing result
        Result.objects.create(
            student=self.student1,
            session=self.session,
            term=self.term,
            current_class=self.student_class,
            subject=self.subject1,
            test_score=50,
            exam_score=60,
        )

        url = reverse("create-result")
        student_ids = f"{self.student1.id}"

        response = self.client.post(
            url,
            {
                "finish": "true",
                "session": self.session.id,
                "term": self.term.id,
                "subjects": [self.subject1.id, self.subject2.id],
                "students": student_ids,
            },
        )

        # Should redirect
        self.assertEqual(response.status_code, 302)

        # Should only create 1 new result (subject2), not duplicate subject1
        results = Result.objects.filter(student=self.student1)
        self.assertEqual(results.count(), 2)

        # Verify the existing result wasn't duplicated
        subject1_results = Result.objects.filter(
            student=self.student1, subject=self.subject1
        )
        self.assertEqual(subject1_results.count(), 1)

    def test_create_result_only_for_students_with_class(self):
        """Verifica se apenas cria resultados para alunos com turma definida"""
        url = reverse("create-result")
        # Try to create results for student3 who has no class
        student_ids = f"{self.student3.id}"

        response = self.client.post(
            url,
            {
                "finish": "true",
                "session": self.session.id,
                "term": self.term.id,
                "subjects": [self.subject1.id],
                "students": student_ids,
            },
        )

        # Should redirect
        self.assertEqual(response.status_code, 302)

        # No results should be created for student3
        results = Result.objects.filter(student=self.student3)
        self.assertEqual(results.count(), 0)

    def test_create_result_requires_login(self):
        """Verifica que a view requer login"""
        self.client.logout()
        url = reverse("create-result")
        response = self.client.get(url)

        # Should redirect to login
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith("/accounts/login/"))


class EditResultsViewTest(TestCase):
    def setUp(self):
        """Set up test fixtures"""
        self.client = Client()
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.client.login(username="testuser", password="testpass")

        # Create academic session and term
        self.session = AcademicSession.objects.create(
            name="2024/2025", current=True
        )
        self.term = AcademicTerm.objects.create(name="First Term", current=True)

        # Create other data
        self.subject, _ = Subject.objects.get_or_create(name="Mathematics")
        self.student_class, _ = StudentClass.objects.get_or_create(name="Grade 10")
        self.student = Student.objects.create(
            registration_number="STU001",
            surname="Doe",
            firstname="John",
            current_class=self.student_class,
        )

        # Create a result
        self.result = Result.objects.create(
            student=self.student,
            session=self.session,
            term=self.term,
            current_class=self.student_class,
            subject=self.subject,
            test_score=50,
            exam_score=60,
        )

    def test_edit_results_GET_displays_correctly(self):
        """Verifica exibição da view de edição de resultados"""
        url = reverse("edit-results")
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "result/edit_results.html")
        self.assertIn("formset", response.context)

    def test_edit_results_requires_login(self):
        """Verifica que a view requer login"""
        self.client.logout()
        url = reverse("edit-results")
        response = self.client.get(url)

        # Should redirect to login
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith("/accounts/login/"))


class ResultListViewTest(TestCase):
    def setUp(self):
        """Set up test fixtures"""
        self.client = Client()
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.client.login(username="testuser", password="testpass")

        # Create academic session and term
        self.session = AcademicSession.objects.create(
            name="2024/2025", current=True
        )
        self.term = AcademicTerm.objects.create(name="First Term", current=True)

        # Create other data
        self.subject1, _ = Subject.objects.get_or_create(name="Mathematics")
        self.subject2, _ = Subject.objects.get_or_create(name="English")
        self.student_class, _ = StudentClass.objects.get_or_create(name="Grade 10")
        self.student = Student.objects.create(
            registration_number="STU001",
            surname="Doe",
            firstname="John",
            current_class=self.student_class,
        )

        # Create results
        self.result1 = Result.objects.create(
            student=self.student,
            session=self.session,
            term=self.term,
            current_class=self.student_class,
            subject=self.subject1,
            test_score=30,
            exam_score=50,
        )
        self.result2 = Result.objects.create(
            student=self.student,
            session=self.session,
            term=self.term,
            current_class=self.student_class,
            subject=self.subject2,
            test_score=40,
            exam_score=45,
        )

    def test_result_list_view_shows_all_information(self):
        """Verifica se a view de lista exibe todas as informações"""
        url = reverse("view-results")
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "result/all_results.html")
        self.assertIn("results", response.context)

        # Check that totals are calculated correctly
        results_dict = response.context["results"]
        student_data = results_dict[self.student.id]

        self.assertEqual(student_data["test_total"], 70)  # 30 + 40
        self.assertEqual(student_data["exam_total"], 95)  # 50 + 45
        self.assertEqual(student_data["total_total"], 165)  # 70 + 95
        self.assertEqual(len(student_data["subjects"]), 2)

    def test_result_list_view_requires_login(self):
        """Verifica que a view requer login"""
        self.client.logout()
        url = reverse("view-results")
        response = self.client.get(url)

        # Should redirect to login
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith("/accounts/login/"))
