import datetime as dt

from django.db.models import Avg

from rest_framework import serializers

from reviews.models import Comment, Review, Category, Genre, Title


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


class TitleSerializer(serializers.ModelSerializer):
    rating = serializers.SerializerMethodField()

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
        return obj.reviews.aggregate(rating=Avg("score"))

    def validate_year(self, value):
        year = dt.date.today().year
        if not (0 < value <= year):
            raise serializers.ValidationError("Проверьте год произведения!")
        return value


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        read_only=True, slug_field='username',
    )

    class Meta:
        fields = '__all__'
        read_only_fields = ('title',)
        model = Review

    def validate(self, data):
        """осуществляется проверка, оставлял ли автор уже на
        данное произведение отзыв или нет. Если оставлял - выдается ошибка"""
        title = self.initial_data.get('title')
        author = self.initial_data.get('author')

        if Review.objects.filter(title=title, author=author).exists():
            raise serializers.ValidationError({
                'message': 'Автор уже оставлял отзыв на это призведение!'
            })

        return data



class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        read_only=True, slug_field='username'
    )

    class Meta:
        fields = ('id', 'text', 'author', 'pub_date')
        model = Comment
