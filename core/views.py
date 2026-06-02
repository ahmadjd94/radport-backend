from rest_framework.decorators import api_view

from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.status import HTTP_404_NOT_FOUND
from .models import StudyReport, Flow
from .serializers import EnrichedChecklistSerializer, StudyReportSerializer, FlowSerializer



@api_view(http_method_names=["GET"])
def retrieve_flow(request, flow_type, ):
    target_object = Flow.objects.filter(flow_type="CXR").first()
    data = FlowSerializer(target_object)
    return Response(data.data)


@api_view(http_method_names=["POST"])
def create_flow(request):
    Flow.objects.filter(flow_type="CXR", is_active=True).update(is_active=False)
    serializer = FlowSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# views.py

from rest_framework import generics, permissions, status
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from django.shortcuts import get_object_or_404


class StudyReportCreateView(generics.CreateAPIView):
    """
    POST /api/reports/
    Creates a new report (draft or submitted) tied to a study_uid.
    Frontend posts the full completed checklist here.
    """
    serializer_class = StudyReportSerializer
    permission_classes = [permissions.IsAuthenticated]


class FlowReportDetailView(generics.RetrieveUpdateAPIView):
    """
    GET  /api/reports/<id>/   — retrieve a saved report
    PATCH /api/reports/<id>/  — update a draft (e.g. resume mid-session)
                                or submit by setting status=submitted
    """
    serializer_class = StudyReportSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return StudyReport.objects.filter(submitted_by=self.request.user)

    # def partial_update(self, request, *args, **kwargs):
    #     instance = self.get_object()
    #     if instance.status == FlowReport.Status.SUBMITTED:
    #         raise PermissionDenied("A submitted report cannot be modified.")
    #     kwargs["partial"] = True
    #     return self.update(request, *args, **kwargs)


class StudyReportByStudyView(generics.ListAPIView):
    """
    GET /api/reports/study/<study_uid>/
    Returns all reports for a given study_uid.
    Frontend calls this when opening a study to check for existing reports.
    """
    serializer_class = StudyReportSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return StudyReport.objects.filter(
            study_uid=self.kwargs["study_uid"]
        ).select_related("flow", "submitted_by")


class StudyReportViewSet(viewsets.ModelViewSet):
    queryset = StudyReport.objects.select_related('flow')

    @action(detail=False, methods=['get'])
    def get_checklist_with_answers(self, request,study_uid):
        """
        GET /api/reports/get_checklist_with_answers/?study_uid=<uid>

        Returns merged Flow structure + StudyReport answers.
        """

        if not study_uid:
            return Response(
                {'error': 'study_uid query parameter required'},
                status=400
            )

        try:
            report = StudyReport.objects.select_related('flow').get(
                study_uid=study_uid
            )
        except StudyReport.DoesNotExist:
            return Response(
                {'error': f'No report found for study_uid={study_uid}'},
                status=HTTP_404_NOT_FOUND
            )

        serializer = EnrichedChecklistSerializer(report)
        return Response(serializer.data)

    @action(detail='pk', methods=['get'])
    def checklist_by_report_id(self, request, pk=None):
        """
        GET /api/reports/{report_id}/checklist_by_report_id/

        Fetch by StudyReport UUID.
        """
        try:
            report = StudyReport.objects.select_related('flow').get(pk=pk)
        except StudyReport.DoesNotExist:
            return Response(
                {'error': f'Report {pk} not found'},
                status=HTTP_404_NOT_FOUND
            )

        serializer = EnrichedChecklistSerializer(report)
        return Response(serializer.data)