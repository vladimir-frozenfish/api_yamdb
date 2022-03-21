import datetime as dt
import re

from django.db.models import Avg

from rest_framework import serializers

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
        elif not re.search(r"^\w+$", value):
            raise serializers.ValidationError(
                "Username должен состоять из букв, цифр и символа '_'"
            )
        elif value == "me":
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
    rating = serializers.SerializerMethodField()
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

    def get_rating(self, obj):
        if obj.reviews:
            return obj.reviews.all().aggregate(Avg("score"))["score__avg"]
        return None


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

    def validate(self, data):
        title = self.initial_data.get("title")
        author = self.initial_data.get("author")

        if Review.objects.filter(title=title, author=author).exists():
            raise serializers.ValidationError(
                {"message": "Автор уже оставлял отзыв на это призведение!"}
            )

        return data


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        read_only=True, slug_field="username"
    )

    class Meta:
        fields = ("id", "text", "author", "pub_date")
        model = Comment
