import re

from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator
from reviews.models import Comment, Review, User


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        fields = (
            'bio', 'email', 'first_name', 'last_name', 'role', 'username')
        model = User
        
    def validate_username(self, value):
        if value is None:
            raise serializers.ValidationError('Вы не указали username')
        elif not re.search(r'^\w+$', value):
            raise serializers.ValidationError('Username должен состоять из букв, цифр и символа подчеркивания')
        elif value == 'me':
            raise serializers.ValidationError('Пользователь "me" запрещен. Имя зарезервировано.')
        return value

class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        read_only=True, slug_field='username'
    )

    class Meta:
        fields = ('id', 'text', 'author', 'score', 'pub_date')
        model = Review

        validators = [
            UniqueTogetherValidator(
                queryset=Review.objects.all(),
                fields=('author', 'title'),
                message='Можно оставить только один отзыв на произведение'
            )
        ]


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        read_only=True, slug_field='username'
    )

    class Meta:
        fields = ('id', 'text', 'author', 'pub_date')
        model = Comment
