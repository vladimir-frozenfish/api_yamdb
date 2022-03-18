from django.urls import path, include

from rest_framework import routers

from rest_framework_simplejwt.views import TokenObtainPairView

from .views import CommentViewSet, ReviewViewSet, get_token

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
    path('v1/auth/token/', get_token),
]
