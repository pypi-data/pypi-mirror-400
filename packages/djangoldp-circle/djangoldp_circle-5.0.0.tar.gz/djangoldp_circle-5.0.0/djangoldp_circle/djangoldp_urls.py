from django.urls import path
from .views import CirclesJoinableViewset
from .models import Circle
from djangoldp.models import Model


urlpatterns = [
    path('circles/joinable/', CirclesJoinableViewset.urls(model_prefix="circles-joinable",
        model=Circle,
        lookup_field=getattr(Circle._meta, 'lookup_field', 'pk'),
        permission_classes=getattr(Circle._meta, 'permission_classes', []),
        fields=getattr(Circle._meta, 'serializer_fields', []),
        nested_fields=getattr(Circle._meta, 'nested_fields', []))),
]
