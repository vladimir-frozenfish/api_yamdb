from django.shortcuts import get_object_or_404
from django.contrib.auth import authenticate

from rest_framework.response import Response
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import api_view, permission_classes

from rest_framework_simplejwt.tokens import AccessToken

from reviews.models import Comment, Review, Title, User

from .serializers import CommentSerializer, ReviewSerializer


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def get_token(request):
    username = request.data.get('username')
    if username is None:
        return Response({'Сообщение': 'Заполните поля'}, status=status.HTTP_400_BAD_REQUEST)

    user = get_object_or_404(User, username=username)
    password = request.data['confirmation_code']
    user = authenticate(username=user, password=password)

    if user:
        token = AccessToken.for_user(user)
        return Response({'access': str(token)}, status=status.HTTP_200_OK)

    return Response({'Сообщение': 'Неправильный confirmation_code'}, status=status.HTTP_400_BAD_REQUEST)


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        title_id = self.kwargs.get("title_id")
        title = get_object_or_404(Title, id=title_id)
        new_queryset = title.reviews.all()
        return new_queryset


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        review_id = self.kwargs.get("review_id")
        review = get_object_or_404(Review, id=review_id)
        new_queryset = review.comments.all()
        return new_queryset