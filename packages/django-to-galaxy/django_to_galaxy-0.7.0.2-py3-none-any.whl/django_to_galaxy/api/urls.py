from django.urls import path
from rest_framework import routers

from django_to_galaxy.api.views.create_history import CreateHistoryView
from django_to_galaxy.api.views.galaxy_instance import GalaxyInstanceViewSet
from django_to_galaxy.api.views.galaxy_output_file import GalaxyOutputFileViewSet
from django_to_galaxy.api.views.galaxy_user import GalaxyUserViewSet
from django_to_galaxy.api.views.history import HistoryViewSet
from django_to_galaxy.api.views.invocation import (
    InvocationViewSet,
    UpdateOutputFilesView,
)
from django_to_galaxy.api.views.workflow import WorkflowViewSet
from django_to_galaxy.api.views.upload_to_history import UploadToHistoryView
from django_to_galaxy.api.views.invoke_workflow import (
    InvokeWorkflowView,
    GetWorkflowDatamapTemplateView,
    # GetWorkflowInputsView,
    ExecuteWorkflowView,
)
from django_to_galaxy.api.views.create_dataset_collection import (
    CreateDatasetListCollectionView,
    CreateDatasetListPairedCollectionView,
    CreateDatasetPairedCollectionView,
)

api_router = routers.DefaultRouter()
api_router.register(r"instances", GalaxyInstanceViewSet)
api_router.register(r"galaxy_output_files", GalaxyOutputFileViewSet)
api_router.register(r"galaxy_users", GalaxyUserViewSet)
api_router.register(r"histories", HistoryViewSet)
api_router.register(r"invocations", InvocationViewSet)
api_router.register(r"workflows", WorkflowViewSet)

urlpatterns = [
    path("create_history/<int:pk>", CreateHistoryView.as_view()),
    path("upload_to_history/", UploadToHistoryView.as_view()),
    path("invoke_workflow/", InvokeWorkflowView.as_view()),
    path("execute_workflow/", ExecuteWorkflowView.as_view()),
    path("update_galaxy_output_files/<int:pk>", UpdateOutputFilesView.as_view()),
    path("get_datamap_template/<int:pk>", GetWorkflowDatamapTemplateView.as_view()),
    path(
        "create_dataset_collection_paired/", CreateDatasetPairedCollectionView.as_view()
    ),
    path("create_dataset_collection_list/", CreateDatasetListCollectionView.as_view()),
    path(
        "create_dataset_collection_list_paired/",
        CreateDatasetListPairedCollectionView.as_view(),
    ),
    # path("get_workflow_inputs/<int:pk>", GetWorkflowInputsView.as_view()),
]

urlpatterns += api_router.urls
