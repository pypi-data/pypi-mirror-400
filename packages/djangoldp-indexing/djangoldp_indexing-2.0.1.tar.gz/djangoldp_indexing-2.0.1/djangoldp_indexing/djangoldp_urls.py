from django.urls import path, re_path
from django.db.models import Model

from .views.instance.root import InstanceRootContainerView
from .views.instance.webid import InstanceWebIDView
from .views.instance.type_index import PublicTypeIndexView
from .views.instance.indexes import InstanceIndexesRootView
from .views.static import serve_static_profile, serve_static_fedex, serve_static_index
from .views.model.root import ModelRootIndexView
from .views.model.property import ModelPropertyIndexView
from .views.model.pattern import ModelPropertyPatternIndexView

def get_all_non_abstract_subclasses(cls):
    """Returns all non-abstract subclasses of a class"""
    def valid_subclass(sc):
        return not getattr(sc._meta, 'abstract', False)
    
    return set(c for c in cls.__subclasses__() if valid_subclass(c)).union(
        [subclass for c in cls.__subclasses__() 
         for subclass in get_all_non_abstract_subclasses(c) if valid_subclass(subclass)])

# Base indexing routes
urlpatterns = [
    path('indexes/', InstanceIndexesRootView.as_view(), name='indexes-root'),
    path('fedex/profile', serve_static_profile, name='static-profile'),
    re_path(r'^fedex/profile/(?P<path>.+)$', serve_static_profile, name='static-profile-file'),
    re_path(r'^fedex/(?P<path>.+)/index$', serve_static_fedex, name='static-fedex'),
    re_path(r'^indexes/(?P<path>.+)$', serve_static_index, name='static-indexes'),
]
