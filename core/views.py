from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import Job
from .serializers import RegisterSerializer, JobSerializer


# ---------------------------------------------------------
# 1. USER REGISTRATION (SIGNUP)
# ---------------------------------------------------------
class RegisterView(APIView):

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "User registered successfully!"}, 
                status=status.HTTP_201_CREATED
            )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



# ---------------------------------------------------------
# 2. CREATE JOB (RECRUITERS ONLY)
# ---------------------------------------------------------
class CreateJobView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Check if user is recruiter
        if request.user.role != "recruiter":
            return Response(
                {"error": "Only recruiters can post jobs."},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = JobSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(posted_by=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



# ---------------------------------------------------------
# 3. LIST JOBS + SEARCH
# ---------------------------------------------------------
from .models import Job, Application
from .serializers import ApplicationSerializer
class JobListView(APIView):

    def get(self, request):
        jobs = Job.objects.all().order_by("-created_at")

        # If search query exists → apply filter
        search = request.GET.get("search")
        if search:
            jobs = jobs.filter(title__icontains=search)

        serializer = JobSerializer(jobs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
# ---------------------------------------------------------
# 4. APPLY TO JOB (CANDIDATES ONLY)     
class ApplyJobView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, job_id):
        # Only candidates can apply
        if request.user.role != "candidate":
            return Response(
                {"error": "Only candidates can apply."},
                status=status.HTTP_403_FORBIDDEN
            )

        # Check job exists
        try:
            job = Job.objects.get(id=job_id)
        except Job.DoesNotExist:
            return Response(
                {"error": "Job not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        # Prevent duplicate applications
        if Application.objects.filter(job=job, candidate=request.user).exists():
            return Response(
                {"error": "You already applied to this job"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Create application
        application = Application.objects.create(
            job=job,
            candidate=request.user
        )

        serializer = ApplicationSerializer(application)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
class MyApplicationsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        apps = Application.objects.filter(candidate=request.user)
        serializer = ApplicationSerializer(apps, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
class ViewApplicantsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, job_id):
        if request.user.role != "recruiter":
            return Response(
                {"error": "Only recruiters can view applicants"},
                status=status.HTTP_403_FORBIDDEN
            )

        try:
            job = Job.objects.get(id=job_id, posted_by=request.user)
        except Job.DoesNotExist:
            return Response(
                {"error": "Job not found or not posted by you"},
                status=status.HTTP_404_NOT_FOUND
            )

        applicants = Application.objects.filter(job=job)
        serializer = ApplicationSerializer(applicants, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
class UpdateApplicationStatusView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, app_id):
        if request.user.role != "recruiter":
            return Response(
                {"error": "Only recruiters can update status"},
                status=status.HTTP_403_FORBIDDEN
            )

        try:
            application = Application.objects.get(id=app_id)
        except Application.DoesNotExist:
            return Response(
                {"error": "Application not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        new_status = request.data.get("status")
        if new_status not in ["accepted", "rejected"]:
            return Response(
                {"error": "Status must be 'accepted' or 'rejected'"},
                status=status.HTTP_400_BAD_REQUEST
            )

        application.status = new_status
        application.save()

        serializer = ApplicationSerializer(application)
        return Response(serializer.data, status=status.HTTP_200_OK)


