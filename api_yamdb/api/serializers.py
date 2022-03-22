import datetime as dt
import re

from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator
from reviews.models import Category, Comment, Genre, Review, Title, User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        fields = (
            "bio",
            "email",
            "first_name",
            "last_name",
            "role",
            "username",
        )
        model = User

    def validate_username(self, value):
        if value is None:
            raise serializers.ValidationError("Вы не указали username")
        if not re.search(r"^\w+$", value):
            raise serializers.ValidationError(
                "Username должен состоять из букв, цифр и символа '_'"
            )
        if value == "me":
            raise serializers.ValidationError(
                'Пользователь "me" запрещен. Имя зарезервировано.'
            )
        return value


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ("name", "slug")
        lookup_field = "slug"


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ("name", "slug")
        lookup_field = "slug"


class TitleGetSerializer(serializers.ModelSerializer):
    rating = serializers.IntegerField(read_only=True)
    category = CategorySerializer(read_only=True)
    genre = GenreSerializer(read_only=True, many=True)

    class Meta:
        model = Title
        fields = (
            "id",
            "name",
            "year",
            "rating",
            "description",
            "category",
            "genre",
        )


class TitleSerializer(serializers.ModelSerializer):
    category = serializers.SlugRelatedField(
        queryset=Category.objects.all(), slug_field="slug"
    )
    genre = serializers.SlugRelatedField(
        queryset=Genre.objects.all(), many=True, slug_field="slug"
    )

    class Meta:
        model = Title
        fields = (
            "id",
            "name",
            "year",
            "description",
            "category",
            "genre",
        )

    def validate_year(self, value):
        year = dt.date.today().year
        if not (0 < value <= year):
            raise serializers.ValidationError("Проверьте год произведения!")
        return value


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        read_only=True, slug_field="username"
    )

    class Meta:
        fields = ("id", "author", "text", "score", "pub_date")
        read_only_fields = ("title",)
        model = Review


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        read_only=True, slug_field="username"
    )

    class Meta:
        fields = ("id", "text", "author", "pub_date")
        model = Comment


class SendCodeSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True, max_length=150)
    username = serializers.CharField(required=True,)

    class Meta:
        model = User
        fields = (
            'username', 'email', 'first_name', 'last_name', 'bio', 'role',
        )
        validators = [
            UniqueTogetherValidator(
                queryset=User.objects.all(),
                fields=('email',),
                message='Почтовый адресс уже используется'
            ),
            UniqueTogetherValidator(
                queryset=User.objects.all(),
                fields=('username',),
                message='Имя пользователя уже используется'
            )
        ]


class ConfirmationCodeSerializer(serializers.Serializer):
    confirmation_code = serializers.CharField(required=True)
    username = serializers.CharField(required=True, max_length=150)
