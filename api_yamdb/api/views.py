import uuid
from smtplib import SMTPException

from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, mixins, permissions, status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken

from api_yamdb.settings import SERVICE_EMAIL
from reviews.models import Category, Genre, Review, Title, User
from .filters import TitleFilter
from .permissions import (IsAdmin, IsAdminOrReadOnly,
                          IsAuthorAdminModeratorOrReadOnly,
                          IsSuperuser)
from .serializers import (CategorySerializer, CommentSerializer,
                          ConfirmationCodeSerializer, GenreSerializer,
                          ReviewSerializer, SendCodeSerializer,
                          TitleGetSerializer, TitleSerializer, UserSerializer)


@api_view(["POST"])
@permission_classes([permissions.AllowAny])
def send_register_code(request):
    serializer = SendCodeSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    username = serializer.validated_data['username']
    email = serializer.validated_data['email']
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
    serializer = ConfirmationCodeSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    username = serializer.validated_data['username']
    confirmation_code = serializer.validated_data['confirmation_code']

    if not username:
        raise ValidationError({"username": "Неправльное имя пользовтеля"})

    user = get_object_or_404(User, username=username)

    if not default_token_generator.check_token(user, confirmation_code):
        raise ValidationError(
            {"confirmation_code": "Неправильный код подтверждения"}
        )

    token = AccessToken.for_user(user)
    return Response({"token": str(token)}, status=status.HTTP_200_OK)


class UserViewSet(viewsets.ModelViewSet):
    permission_classes = [IsSuperuser | IsAdmin, permissions.IsAuthenticated]
    queryset = User.objects.all()
    serializer_class = UserSerializer
    lookup_field = "username"
    filter_backends = [filters.SearchFilter]
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
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ("name",)
    lookup_field = "slug"


class CategoryViewSet(ListCreateDeleteViewSet):
    queryset = Category.objects.all().order_by("name")
    serializer_class = CategorySerializer


class GenreViewSet(ListCreateDeleteViewSet):
    queryset = Genre.objects.all().order_by("name")
    serializer_class = GenreSerializer


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.annotate(
        rating=Avg("reviews__score")).order_by("name")
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_class = TitleFilter

    def get_serializer_class(self):
        if self.request.method == "GET":
            return TitleGetSerializer
        return TitleSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = [
        permissions.IsAuthenticatedOrReadOnly,
        IsAuthorAdminModeratorOrReadOnly,
    ]

    def get_queryset(self):
        title_id = self.kwargs.get("title_id")
        title = get_object_or_404(Title, id=title_id)
        new_queryset = title.reviews.all().order_by("pub_date")
        return new_queryset

    def perform_create(self, serializer):
        user = self.request.user
        title_id = self.kwargs.get("title_id")
        title = get_object_or_404(Title, id=title_id)
        serializer.save(author=user, title=title)


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [
        permissions.IsAuthenticatedOrReadOnly,
        IsAuthorAdminModeratorOrReadOnly,
    ]

    def get_queryset(self):
        review_id = self.kwargs.get("review_id")
        title_id = self.kwargs.get("title_id")
        review = get_object_or_404(Review, id=review_id, title=title_id)
        new_queryset = review.comments.all().order_by("pub_date")
        return new_queryset

    def perform_create(self, serializer):
        review_id = self.kwargs.get("review_id")
        title_id = self.kwargs.get("title_id")
        review = get_object_or_404(Review, id=review_id, title=title_id)
        serializer.save(author=self.request.user, review=review)
