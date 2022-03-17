from django.urls import path, include

from rest_framework import routers

from .views import CommentViewSet, ReviewViewSet

app_name = 'api'

router = routers.DefaultRouter()

router.register(
    r'titles/(?P<title_id>\d+)/reviews', ReviewViewSet, basename='reviews'
)
router.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments', CommentViewSet, basename='reviews'
)


urlpatterns = [
    path('v1/', include(router.urls)),
]
