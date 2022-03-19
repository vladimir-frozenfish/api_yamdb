from django.urls import path, include

from rest_framework import routers

from .views import (
    CommentViewSet,
    ReviewViewSet,
    CategoryViewSet,
    GenreViewSet,
    TitleViewSet,
    get_token,
    send_register_code,
    UserViewSet
)

app_name = 'api'

router = routers.DefaultRouter()

router.register('users', UserViewSet, basename='users')
router.register(
    r'titles/(?P<title_id>\d+)/reviews', ReviewViewSet, basename='reviews'
)
router.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments', CommentViewSet, basename='reviews'
)
router.register("categories", CategoryViewSet)
router.register("genres", GenreViewSet)
router.register("titles", TitleViewSet)

v1_auth = [path('signup/', send_register_code, name='register'),
                  path('token/', get_token, name='get_token'), ]

urlpatterns = [
    path('v1/', include(router.urls)),
    path('v1/auth/', include(v1_auth)),
]