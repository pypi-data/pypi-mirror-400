from django.urls import path
from .views import OpenCommunitiesViewset
from .models import Community
from djangoldp.models import Model

urlpatterns = [
    path('open-communities/', OpenCommunitiesViewset.urls(model_prefix="open-communities",
        model=Community,
        lookup_field=getattr(Community._meta, 'lookup_field', 'pk'),
        permission_classes=getattr(Community._meta, 'permission_classes', []),
        fields=getattr(Community._meta, 'serializer_fields', []),
        nested_fields=getattr(Community._meta, 'nested_fields', [])))
]
