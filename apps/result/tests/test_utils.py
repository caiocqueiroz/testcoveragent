from django.test import TestCase

from apps.result.utils import score_grade


class ScoreGradeTest(TestCase):
    def test_score_grade_returns_A_for_scores_80_to_100(self):
        """Verifica se retorna 'A' para pontuações de 80 a 100"""
        self.assertEqual(score_grade(80), "A")
        self.assertEqual(score_grade(90), "A")
        self.assertEqual(score_grade(100), "A")

    def test_score_grade_returns_B_for_scores_70_to_79(self):
        """Verifica se retorna 'B' para pontuações de 70 a 79"""
        self.assertEqual(score_grade(70), "B")
        self.assertEqual(score_grade(75), "B")
        self.assertEqual(score_grade(79), "B")

    def test_score_grade_returns_C_for_scores_60_to_69(self):
        """Verifica se retorna 'C' para pontuações de 60 a 69"""
        self.assertEqual(score_grade(60), "C")
        self.assertEqual(score_grade(65), "C")
        self.assertEqual(score_grade(69), "C")

    def test_score_grade_returns_D_for_scores_50_to_59(self):
        """Verifica se retorna 'D' para pontuações de 50 a 59"""
        self.assertEqual(score_grade(50), "D")
        self.assertEqual(score_grade(55), "D")
        self.assertEqual(score_grade(59), "D")

    def test_score_grade_returns_E_for_scores_40_to_49(self):
        """Verifica se retorna 'E' para pontuações de 40 a 49"""
        self.assertEqual(score_grade(40), "E")
        self.assertEqual(score_grade(45), "E")
        self.assertEqual(score_grade(49), "E")

    def test_score_grade_returns_F_for_failing_scores(self):
        """Verifica se retorna 'F' para pontuações reprovadas (0-39)"""
        self.assertEqual(score_grade(0), "F")
        self.assertEqual(score_grade(10), "F")
        self.assertEqual(score_grade(20), "F")
        self.assertEqual(score_grade(39), "F")

    def test_score_grade_handles_edge_cases(self):
        """Verifica comportamento para valores nos limites das faixas"""
        # Test boundary values
        self.assertEqual(score_grade(39), "F")  # Just below E
        self.assertEqual(score_grade(40), "E")  # Start of E
        self.assertEqual(score_grade(49), "E")  # End of E
        self.assertEqual(score_grade(50), "D")  # Start of D
        self.assertEqual(score_grade(59), "D")  # End of D
        self.assertEqual(score_grade(60), "C")  # Start of C
        self.assertEqual(score_grade(69), "C")  # End of C
        self.assertEqual(score_grade(70), "B")  # Start of B
        self.assertEqual(score_grade(79), "B")  # End of B
        self.assertEqual(score_grade(80), "A")  # Start of A

    def test_score_grade_handles_negative_values(self):
        """Verifica comportamento para valores negativos"""
        self.assertEqual(score_grade(-1), "F")
        self.assertEqual(score_grade(-10), "F")

    def test_score_grade_handles_values_above_100(self):
        """Verifica comportamento para valores acima de 100"""
        self.assertEqual(score_grade(101), "A")
        self.assertEqual(score_grade(150), "A")
