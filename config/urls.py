from django.contrib import admin
from django.urls import path
from django.http import JsonResponse

# Authentication
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

# App views
from core.views import (
    RegisterView,
    CreateJobView,
    JobListView,
    ApplyJobView,
    MyApplicationsView,
    ViewApplicantsView,
    UpdateApplicationStatusView,
)

urlpatterns = [
    # Home
    path('', lambda request: JsonResponse({"message": "Job Portal API is running"})),

    # Admin
    path('admin/', admin.site.urls),

    # Authentication
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Jobs
    path('jobs/create/', CreateJobView.as_view(), name='create_job'),
    path('jobs/', JobListView.as_view(), name='list_jobs'),

    # Applications
    path('jobs/<int:job_id>/apply/', ApplyJobView.as_view(), name='apply_job'),
    path('applications/me/', MyApplicationsView.as_view(), name='my_applications'),

    # Recruiter
    path('jobs/<int:job_id>/applicants/', ViewApplicantsView.as_view(), name='view_applicants'),
    path('applications/<int:app_id>/update/', UpdateApplicationStatusView.as_view(), name='update_application'),
]
