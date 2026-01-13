from django.urls import path
from .views import ProjectsJoinableViewset
from .models import Project
from djangoldp.models import Model


urlpatterns = [
    path('projects/joinable/', ProjectsJoinableViewset.urls(model_prefix="projects-joinable",
        model=Project,
        lookup_field=getattr(Project._meta, 'lookup_field', 'pk'),
        permission_classes=getattr(Project._meta, 'permission_classes', []),
        fields=getattr(Project._meta, 'serializer_fields', []),
        nested_fields=getattr(Project._meta, 'nested_fields', [])))
]
