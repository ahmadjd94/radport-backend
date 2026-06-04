
from .serializers import CustomTokenObtainPairView

from django.urls import path,include
from rest_framework_simplejwt.views import (
    TokenRefreshView,         # For getting a new access token using the refresh token
)

from .views import retrieve_flow, create_flow, study_report_create_view, StudyReportViewSet, StudyReportByStudyView

urlpatterns = [
    path('api/flows/<str:flow_type>', retrieve_flow),
    path('api/flows/', create_flow),
    path('api/study/<str:study_uid>/flow', study_report_create_view, name="create-study-flow"),
    path('api/study/<str:study_uid>/', StudyReportViewSet.as_view({'get': 'get_checklist_with_answers'}), name="study-flow"),
    path("reports/study/<str:study_uid>/", StudyReportByStudyView.as_view(), name="report-by-study"),
    path("pacs/", include("core.pacs.urls")),
    path('api/token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]

