from django.urls import path
from . import views

urlpatterns = [

    # LOGIN & HOME
    path('', views.login_view, name='login'),
    path('home/', views.home, name='home'),

    # CANDIDATE MODULE
    path('add/', views.add_candidate, name='add_candidate'),
    path('candidates/', views.candidate_list, name='candidate_list'),
    path(
    'delete-candidate/<int:candidate_id>/',
    views.delete_candidate,
    name='delete_candidate'),

    # RESUME UPLOAD
    path('upload/', views.upload_resume, name='upload_resume'),

    # INTERVIEW FLOW
    path('start/<int:resume_id>/', views.start_interview, name='start_interview'),
    path('live/<int:session_id>/', views.live_interview, name='live_interview'),

    # INTERVIEW COMPLETE
    path('complete/<int:session_id>/', views.interview_complete, name='interview_complete'),

    # RESULT PAGE
    path('result/<int:session_id>/', views.final_result, name='final_result'),

    # CERTIFICATE DOWNLOAD
   path(
    'certificate/<int:session_id>/',
    views.download_certificate,
    name='download_certificate'
),
    path(
    'interview-results/',
    views.interview_results,
    name='interview_results'
),
    path(
    'delete-interview-result/<int:session_id>/',
    views.delete_interview_result,
    name='delete_interview_result'
),
    
    path(
    'candidate/edit/<int:id>/',
    views.edit_candidate,
    name='edit_candidate'
),
    path(
    'result/edit/<int:id>/',
    views.edit_result,
    name='edit_result'
),

path(
    'my-result/',
    views.my_result,
    name='my_result'
),
]