from django.shortcuts import get_object_or_404
from django.contrib.auth import authenticate

from rest_framework.response import Response
from rest_framework import viewsets, mixins, filters, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework_simplejwt.tokens import AccessToken

from django_filters.rest_framework import DjangoFilterBackend

from reviews.models import Review, Title, Category, Genre, User
from .permissions import AdminOrReadOnly, IsAuthorOrReadOnly
from .serializers import (
    CommentSerializer,
    ReviewSerializer,
    CategorySerializer,
    GenreSerializer,
    TitleSerializer,
)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def get_token(request):
    """функция получения токена,
    в качестве confirmation_code - используется password"""

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


class ListCreateDeleteViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    pass


class CategoryViewSet(ListCreateDeleteViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (AdminOrReadOnly,)
    filter_backends = [filters.SearchFilter]
    search_fields = ("name",)


class GenreViewSet(ListCreateDeleteViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = (AdminOrReadOnly,)
    filter_backends = [filters.SearchFilter]
    search_fields = ("name",)


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.all()
    serializer_class = TitleSerializer
    permission_classes = (AdminOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ("category__slug", "genre__slug", "name", "year")


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly,
                          IsAuthorOrReadOnly]

    def get_queryset(self):
        title_id = self.kwargs.get("title_id")
        title = get_object_or_404(Title, id=title_id)
        new_queryset = title.reviews.all()
        return new_queryset

    def create(self, request, *args, **kwargs):
        user = self.request.user

        title_id = self.kwargs.get("title_id")
        title = get_object_or_404(Title, id=title_id)

        if Review.objects.filter(title=title, author=user).exists():
            return Response({"message": "Автор уже оставлял отзыв на это призведение"},
                            status=status.HTTP_400_BAD_REQUEST)

        serializer = ReviewSerializer(data=request.data)

        if serializer.is_valid(raise_exception=True):
            serializer.save(author=user, title=title)
            return Response(serializer.data, status=status.HTTP_201_CREATED)


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        review_id = self.kwargs.get("review_id")
        review = get_object_or_404(Review, id=review_id)
        new_queryset = review.comments.all()
        return new_queryset