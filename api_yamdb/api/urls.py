from django.urls import include, path
from rest_framework import routers

from .views import CommentViewSet, ReviewViewSet, get_token, send_register_code, UserViewSet

app_name = 'api'

router = routers.DefaultRouter()

router.register('users', UserViewSet, basename='users')
router.register(
    r'titles/(?P<title_id>\d+)/reviews', ReviewViewSet, basename='reviews'
)
router.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments', CommentViewSet, basename='reviews'
)

v1_auth = [path('signup/', send_register_code, name='register'),
                  path('token/', get_token, name='get_token'), ]

urlpatterns = [
    path('v1/', include(router.urls)),
    path('v1/auth/', include(v1_auth)),
]


'''
from django.urls import path, include

from rest_framework import routers

from .views import CommentViewSet, FollowViewSet, GroupViewSet, PostViewSet

app_name = 'api'

router = routers.DefaultRouter()
router.register('posts', PostViewSet)
router.register('groups', GroupViewSet)
router.register(
    r'posts/(?P<post_id>\d+)/comments', CommentViewSet, basename='comments'
)
router.register('follow', FollowViewSet, basename='follow')


urlpatterns = [
    path('v1/', include(router.urls)),
    path('v1/', include('djoser.urls')),
    path('v1/', include('djoser.urls.jwt')),
]
'''
