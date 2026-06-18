from urllib import request

from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.core.mail import send_mail

from .models import Candidate, Resume, InterviewSession
from .forms import ResumeForm
from .utils import calculate_score

import pdfplumber
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.pagesizes import landscape, A4
from reportlab.pdfgen import canvas
import random
from django.http import HttpResponse
from django.shortcuts import get_object_or_404

from django.conf import settings
import qrcode
import uuid
import os

from datetime import datetime
from django.shortcuts import get_object_or_404, redirect
from .models import InterviewSession

from django.shortcuts import render
from .models import InterviewSession


# =========================
# LOGIN PAGE
# =========================
def login_view(request):

    if request.method == "POST":

        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")

        request.session["username"] = username
        request.session["email"] = email

        # Admin Login
        if username == "admin" and password == "admin123":
            request.session["role"] = "admin"

        # User Login
        else:
            request.session["role"] = "user"

        return redirect("home")

    return render(request, "login.html")


# =========================
# HOME PAGE
# =========================
def home(request):

    total_candidates = Candidate.objects.count()

    total_interviews = InterviewSession.objects.count()

    selected = InterviewSession.objects.filter(
        status="Selected"
    ).count()

    rejected = InterviewSession.objects.filter(
        status="Rejected"
    ).count()

    context = {
        "total_candidates": total_candidates,
        "total_interviews": total_interviews,
        "selected": selected,
        "rejected": rejected,
    }

    return render(
        request,
        "home.html",
        context
    )
# =========================
# ADD CANDIDATE
# =========================
def add_candidate(request):
    if request.method == "POST":
        Candidate.objects.create(
            name=request.POST.get("name"),
            email=request.POST.get("email"),
            department=request.POST.get("department"),
            skills=request.POST.get("skills"),
        )

        return redirect("candidate_list")

    return render(request, "add.html")


# =========================
# CANDIDATE LIST
# =========================
def candidate_list(request):
    query = request.GET.get("q")

    if query:
        candidates = Candidate.objects.filter(
            name__icontains=query
        )
    else:
        candidates = Candidate.objects.all()

    return render(
        request,
        "candidate_list.html",
        {"candidates": candidates}
    )
    
    # =========================
# DELETE CANDIDATE
# =========================
def delete_candidate(request, candidate_id):

    candidate = get_object_or_404(
        Candidate,
        id=candidate_id
    )

    candidate.delete()

    return redirect("candidate_list")


# =========================
# UPLOAD RESUME
# =========================
def upload_resume(request):
    if request.method == "POST":
        form = ResumeForm(
            request.POST,
            request.FILES
        )

        if form.is_valid():
            resume = form.save()

            return redirect(
                "start_interview",
                resume_id=resume.id
            )

    else:
        form = ResumeForm()

    return render(
        request,
        "upload_resume.html",
        {"form": form}
    )
    # =========================
# QUESTION BANK
# =========================
QUESTION_BANK = {

    "python": {
        "easy": [
            "What is Python?",
            "What are Python Data Types?"
        ],
        "medium": [
            "Explain OOP Concepts.",
            "What are Decorators?"
        ],
        "hard": [
            "Explain Multithreading.",
            "Difference between Threading and Multiprocessing?"
        ]
    },

    "django": {
        "easy": [
            "What is Django?"
        ],
        "medium": [
            "Explain Django ORM.",
            "What is MVT Architecture?"
        ],
        "hard": [
            "Explain Middleware.",
            "What are Django Signals?"
        ]
    },

    "sql": {
        "easy": [
            "What is SQL?"
        ],
        "medium": [
            "Explain Normalization.",
            "What are Joins?"
        ],
        "hard": [
            "What are Indexes?",
            "Explain Stored Procedures."
        ]
    },

    "javascript": {
        "easy": [
            "What is JavaScript?"
        ],
        "medium": [
            "Difference between var and let?"
        ],
        "hard": [
            "Explain Closures."
        ]
    }
}


# =========================
# EXTRACT PDF TEXT
# =========================
def extract_text(file_path):
    text = ""

    try:
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()

                if page_text:
                    text += page_text + "\n"

    except Exception as e:
        print("PDF Error:", e)

    return text


# =========================
# GENERATE QUESTIONS
# =========================
def generate_questions(text):

    text = text.lower()

    questions = []

    for skill in QUESTION_BANK:

        if skill in text:

            questions.extend(
                random.sample(
                    QUESTION_BANK[skill]["easy"],
                    min(1, len(QUESTION_BANK[skill]["easy"]))
                )
            )

            questions.extend(
                random.sample(
                    QUESTION_BANK[skill]["medium"],
                    min(1, len(QUESTION_BANK[skill]["medium"]))
                )
            )

            questions.extend(
                random.sample(
                    QUESTION_BANK[skill]["hard"],
                    min(1, len(QUESTION_BANK[skill]["hard"]))
                )
            )

    questions.extend([
        "Tell me about yourself.",
        "What are your strengths?",
        "Why should we hire you?"
    ])

    return list(dict.fromkeys(questions))


# =========================
# START INTERVIEW
# =========================
# =========================
# START INTERVIEW
# =========================
def start_interview(request, resume_id):

    resume = get_object_or_404(
        Resume,
        id=resume_id
    )

    # Save candidate email in session
    
    request.session.modified = True

    Candidate.objects.get_or_create(
        name=resume.name,
        defaults={
            "email": "candidate@gmail.com",
            "department": "Interview Candidate",
            "skills": "Resume Uploaded"
        }
    )

    text = extract_text(
        resume.file.path
    )

    questions = generate_questions(text)

    session = InterviewSession.objects.create(
        resume=resume,
        questions="\n".join(questions),
        current_index=0,
        answers="",
        score=0,
        status="Pending"
    )

    return redirect(
        "live_interview",
        session_id=session.id
    )

# =========================
# LIVE INTERVIEW
# =========================
def live_interview(request, session_id):

    session = get_object_or_404(
        InterviewSession,
        id=session_id
    )

    questions = session.questions.split("\n")

    questions = [
        q for q in questions if q.strip()
    ]

    if session.current_index >= len(questions):
        return redirect(
            "interview_complete",
            session_id=session.id
        )

    current_question = questions[
        session.current_index
    ]

    if request.method == "POST":

        answer = request.POST.get(
            "answer",
            ""
        )

        session.answers += (
            f"Q: {current_question}\n"
            f"A: {answer}\n\n"
        )

        session.score += calculate_score(
            answer
        )

        session.current_index += 1

        session.save()

        return redirect(
            "live_interview",
            session_id=session.id
        )

    return render(
        request,
        "live_interview.html",
        {
            "question": current_question,
            "index": session.current_index + 1,
            "total": len(questions),
        }
    )


# =========================
# INTERVIEW COMPLETE
# =========================
def interview_complete(request, session_id):

    session = get_object_or_404(
        InterviewSession,
        id=session_id
    )

    # Score should never exceed 100
    if session.score > 100:
        session.score = 100
        session.save()

    if session.score >= 80:
        performance = "Excellent"
        status = "Selected"

    elif session.score >= 60:
        performance = "Good"
        status = "Selected"

    elif session.score >= 40:
        performance = "Average"
        status = "Rejected"

    else:
        performance = "Low"
        status = "Rejected"

    session.status = status
    session.save()

    return render(
        request,
        "interview_complete.html",
        {
            "session_id": session.id,
            "score": session.score,
            "status": status,
            "performance": performance,
        }
    )
# =========================
# FINAL RESULT
# =========================
def final_result(request, session_id):

    session = get_object_or_404(
        InterviewSession,
        id=session_id
    )

    if session.score >= 70:
        performance = "Excellent"

    elif session.score >= 50:
        performance = "Good"

    elif session.score >= 30:
        performance = "Average"

    else:
        performance = "Low"

    return render(
    request,
    "interview_result.html",
    {
        "session_id": session.id,
        "score": session.score,
        "status": session.status,
        "performance": performance,
        "answers": session.answers,
    }
)

# =========================
# SEND EMAIL
# =========================
def send_result_email(
    user_email,
    status,
    score
):
    send_mail(
        "Interview Result",
        f"Score: {score}\nStatus: {status}",
        "yourmail@gmail.com",
        [user_email],
        fail_silently=True,
    )


# =========================
# DOWNLOAD CERTIFICATE
# =========================
def download_certificate(request, session_id):

    session = get_object_or_404(
        InterviewSession,
        id=session_id
    )

    candidate_name = session.resume.name
    score = session.score
    status = session.status

    certificate_id = (
        f"AI-{session.id}-"
        f"{uuid.uuid4().hex[:6].upper()}"
    )

    issue_date = datetime.now().strftime(
        "%d-%m-%Y"
    )

    qr = qrcode.make(
        f"Certificate ID:{certificate_id}"
    )

    qr_path = os.path.join(
        settings.MEDIA_ROOT,
        f"qr_{session.id}.png"
    )

    qr.save(qr_path)

    response = HttpResponse(
        content_type='application/pdf'
    )

    response[
        'Content-Disposition'
    ] = (
        f'attachment; filename='
        f'"{candidate_name}_certificate.pdf"'
    )

    p = canvas.Canvas(
        response,
        pagesize=landscape(A4)
    )

    width, height = landscape(A4)

    p.setStrokeColor(colors.darkblue)
    p.setLineWidth(8)

    p.rect(
        20,
        20,
        width-40,
        height-40
    )

    p.setStrokeColor(colors.gold)
    p.setLineWidth(3)

    p.rect(
        35,
        35,
        width-70,
        height-70
    )

    p.setFont(
        "Helvetica-Bold",
        30
    )

    p.drawCentredString(
        width/2,
        height-90,
        "CERTIFICATE OF COMPLETION"
    )

    p.setFont(
        "Helvetica",
        16
    )

    p.drawCentredString(
        width/2,
        height-140,
        "AI Mock Interview Assessment"
    )

    p.setFont(
        "Helvetica-Bold",
        26
    )

    p.drawCentredString(
        width/2,
        height-240,
        candidate_name
    )

    p.setFont(
        "Helvetica",
        16
    )

    p.drawCentredString(
        width/2,
        height-300,
        "Successfully Completed AI Interview"
    )

    p.drawCentredString(
        width/2,
        height-340,
        f"Score : {score}/100"
    )

    p.drawCentredString(
        width/2,
        height-370,
        f"Status : {status}"
    )

    p.drawCentredString(
        width/2,
        height-400,
        f"Certificate ID : {certificate_id}"
    )

    p.drawCentredString(
        width/2,
        height-430,
        f"Issue Date : {issue_date}"
    )

    p.drawImage(
        qr_path,
        80,
        80,
        width=90,
        height=90
    )

    p.save()

    return response
# =========================
# ALL INTERVIEW RESULTS
# =========================
def interview_results(request):

    results = InterviewSession.objects.all().order_by('id')

    return render(
        request,
        "all_interview_results.html",
        {
            "results": results
        }
    )
    
def delete_interview_result(request, session_id):
    session = get_object_or_404(InterviewSession, id=session_id)
    session.delete()
    return redirect('interview_results')

def edit_candidate(request, id):

    candidate = get_object_or_404(
        Candidate,
        id=id
    )

    if request.method == "POST":

        candidate.name = request.POST.get("name")
        candidate.email = request.POST.get("email")
        candidate.department = request.POST.get("department")
        candidate.skills = request.POST.get("skills")

        candidate.save()

        return redirect("candidate_list")

    return render(
        request,
        "edit_candidate.html",
        {"candidate": candidate}
    )
    
def edit_result(request, id):

    result = get_object_or_404(
        InterviewSession,
        id=id
    )

    if request.method == "POST":

        print(request.POST)

        # Score & Status Update
        result.score = request.POST.get("score")
        result.status = request.POST.get("status")

        # Candidate Name Update
        result.resume.name = request.POST.get("candidate_name")

        result.resume.save()
        result.save()

        return redirect("interview_results")

    return render(
        request,
        "edit_result.html",
        {"result": result}
    )
    
def my_result(request):

    email = request.session.get("email")

    if not email:
        return render(request, "my_result.html", {
            "error": "Please login first"
        })

    result = InterviewSession.objects.filter(
        resume__email=email
    ).order_by("-id").first()

    return render(request, "my_result.html", {
        "result": result
    })