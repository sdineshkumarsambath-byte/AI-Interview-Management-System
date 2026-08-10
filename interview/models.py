from django.db import models


# =========================
# CANDIDATE
# =========================
class Candidate(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    department = models.CharField(max_length=100)
    skills = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


# =========================
# QUESTION
# =========================
class Question(models.Model):
    text = models.TextField()
    difficulty = models.CharField(max_length=20, default="easy")

    def __str__(self):
        return self.text


# =========================
# RESUME
# =========================
class Resume(models.Model):
    name = models.CharField(max_length=100)

    email = models.EmailField()

    file = models.FileField(upload_to='resumes/')

    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


# =========================
# INTERVIEW SESSION
# =========================
class InterviewSession(models.Model):
    resume = models.ForeignKey(
        Resume,
        on_delete=models.CASCADE,
        related_name="sessions"
    )

    questions = models.TextField(blank=True, null=True)
    current_index = models.IntegerField(default=0)

    answers = models.TextField(blank=True, null=True)

    score = models.IntegerField(default=0)

    status = models.CharField(
        max_length=20,
        default="Pending"
    )

    feedback = models.TextField(
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.resume.name} - Session {self.id}"