from django.http import Http404
from djangoldp.filters import LocalObjectFilterBackend
from djangoldp.views.ldp_viewset import LDPViewSet
from djangoldp_circle.models import Circle

class CirclesJoinableViewset(LDPViewSet):
    '''Viewset for accessing all Public circles'''
    filter_backends = [LocalObjectFilterBackend]
    def get_queryset(self):
        return Circle.objects.exclude(members__user=self.request.user.id).filter(public=True)