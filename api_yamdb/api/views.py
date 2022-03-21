import uuid
from smtplib import SMTPException

from api_yamdb.settings import SERVICE_EMAIL
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend, FilterSet
from rest_framework import filters, mixins, permissions, status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework.pagination import PageNumberPagination

from reviews.models import Category, Genre, Review, Title, User
from .permissions import (
    IsAdmin,
    IsAdminOrReadOnly,
    IsAuthorOrReadOnly,
    IsSuperuser,
)
from .serializers import (
    CategorySerializer,
    CommentSerializer,
    GenreSerializer,
    ReviewSerializer,
    TitleReadSerializer,
    TitleWriteSerializer,
    UserSerializer,
)


@api_view(["POST"])
@permission_classes([permissions.AllowAny])
def send_register_code(request):
    username = request.data.get("username")
    email = request.data.get("email")
    data = {"username": username, "email": email}
    user_obj = User.objects.filter(
        username=username,
        email=email,
    ).first()
    if user_obj is None:
        serializer = UserSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
    else:
        code = uuid.uuid3(uuid.NAMESPACE_DNS, email)
        User.objects.update(confirmation_code=code)
    confirmation_code = User.objects.get(username=username).confirmation_code
    try:
        send_mail(
            "Служба технического сопровождения YAMDB services",
            f"Привет! Держи свой код доступа {str(confirmation_code)}.",
            SERVICE_EMAIL,
            [email],
            fail_silently=False,
        )
    except SMTPException:
        return Response(
            "Ошибка отправки email", status=status.HTTP_400_BAD_REQUEST
        )
    return Response(data, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes([permissions.AllowAny])
def get_token(request):
    username = request.data.get("username")
    if username is None:
        return Response(
            {"username": "Invalid username"},
            status=status.HTTP_400_BAD_REQUEST,
        )
    user = get_object_or_404(User, username=username)
    if user.confirmation_code != request.data.get("confirmation_code"):
        response = {"confirmation_code": "Invalid confirmation code"}
        return Response(response, status=status.HTTP_400_BAD_REQUEST)
    token = AccessToken.for_user(user)
    return Response({"token": str(token)}, status=status.HTTP_200_OK)


class UserViewSet(viewsets.ModelViewSet):
    permission_classes = (
        IsSuperuser | IsAdmin,
        permissions.IsAuthenticated,
    )
    queryset = User.objects.all()
    serializer_class = UserSerializer
    lookup_field = "username"
    filter_backends = (filters.SearchFilter,)
    search_fields = ("username",)

    @action(
        methods=["GET", "PATCH"],
        url_path="me",
        permission_classes=(permissions.IsAuthenticated,),
        detail=False,
    )
    def get_patch_mixin(self, request):
        if request.method == "GET":
            serializer = self.get_serializer(request.user, many=False)
            return Response(serializer.data, status=status.HTTP_200_OK)
        serializer = self.get_serializer(
            instance=request.user, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save(role=request.user.role)
        return Response(serializer.data, status=status.HTTP_200_OK)


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
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = [filters.SearchFilter]
    search_fields = ("name",)
    lookup_field = "slug"


class GenreViewSet(ListCreateDeleteViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = [filters.SearchFilter]
    search_fields = ("name",)
    lookup_field = "slug"


class TitleFilter(FilterSet):
    class Meta:
        model = Title
        fields = ["category__slug", "genre__slug", "name", "year"]


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.all()
    permission_classes = (IsAdminOrReadOnly,)
    pagination_class = PageNumberPagination
    filter_backends = [DjangoFilterBackend]
    filterset_class = TitleFilter

    def get_serializer_class(self):
        if self.request.method == "GET":
            return TitleReadSerializer
        return TitleWriteSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = [
        permissions.IsAuthenticatedOrReadOnly,
        IsAuthorOrReadOnly,
    ]

    def get_queryset(self):
        title_id = self.kwargs.get("title_id")
        title = get_object_or_404(Title, id=title_id)
        new_queryset = title.reviews.all()
        return new_queryset

    def create(self, request, *args, **kwargs):
        user = self.request.user

        title_id = self.kwargs.get("title_id")
        title = get_object_or_404(Title, id=title_id)

        data = {
            "author": user,
            "title": title,
        }
        data.update(request.data)

        serializer = ReviewSerializer(data=data)

        if serializer.is_valid(raise_exception=True):
            serializer.save(author=user, title=title)
            return Response(serializer.data, status=status.HTTP_201_CREATED)


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer

    def get_queryset(self):
        review_id = self.kwargs.get("review_id")
        review = get_object_or_404(Review, id=review_id)
        new_queryset = review.comments.all()
        return new_queryset
