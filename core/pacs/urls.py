from core.pacs.pacs_views import pacs_proxy
from core.views import retrieve_flow, create_flow, StudyReportByStudyView
from django.urls import path, re_path

urlpatterns = [
    re_path(r"^(?P<path>.*)$", pacs_proxy, name="pacs_proxy"),
]
