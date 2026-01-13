from djangoldp.filters import LocalObjectFilterBackend
from djangoldp.views.ldp_viewset import LDPViewSet
from django.http import Http404

class ProjectsJoinableViewset(LDPViewSet):
    filter_backends = [LocalObjectFilterBackend]

    def get_queryset(self):
        return super().get_queryset().exclude(members__user=self.request.user.id)\
            .exclude(status="Private")\
            .exclude(status="Archived")
