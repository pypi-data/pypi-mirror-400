from django.http import Http404
from djangoldp.views.ldp_viewset import LDPViewSet


class OpenCommunitiesViewset(LDPViewSet):
  def get_queryset(self):
    queryset = super().get_queryset().exclude(allow_self_registration=False)

    # invalidate cache for every open communities
    # unless /open-communities/ is loaded before /communities/xyz/, the last one will get wrong permission nodes
    from djangoldp.models import invalidate_model_cache_if_has_entry
    invalidate_model_cache_if_has_entry(self.model)

    return queryset
