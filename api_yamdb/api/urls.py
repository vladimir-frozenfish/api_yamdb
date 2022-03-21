from django.urls import include, path
from rest_framework import routers

from .views import (
    CategoryViewSet,
    CommentViewSet,
    GenreViewSet,
    ReviewViewSet,
    TitleViewSet,
    UserViewSet,
    get_token,
    send_register_code,
)

app_name = "api"

router = routers.DefaultRouter()

router.register("users", UserViewSet, basename="users")
router.register("categories", CategoryViewSet)
router.register("genres", GenreViewSet)
router.register("titles", TitleViewSet)
router.register(
    r"titles/(?P<title_id>\d+)/reviews", ReviewViewSet, basename="reviews"
)
router.register(
    r"titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments",
    CommentViewSet,
    basename="reviews",
)


v1_auth = [
    path("signup/", send_register_code, name="register"),
    path("token/", get_token, name="get_token"),
]

urlpatterns = [
    path("v1/", include(router.urls)),
    path("v1/auth/", include(v1_auth)),
]
