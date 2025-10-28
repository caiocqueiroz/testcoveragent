def score_grade(score):
    """
    Returns grade based on score.
    Grading scale:
    0-39: F (Fail)
    40-49: E
    50-59: D
    60-69: C
    70-79: B
    80-100: A
    """
    if score >= 80:
        return "A"
    elif score >= 70:
        return "B"
    elif score >= 60:
        return "C"
    elif score >= 50:
        return "D"
    elif score >= 40:
        return "E"
    else:
        return "F"

