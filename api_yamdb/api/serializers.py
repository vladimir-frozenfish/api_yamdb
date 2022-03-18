from django.shortcuts import get_object_or_404

from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

# from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from reviews.models import Comment, Review, Title


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        read_only=True, slug_field='username',
        # default=serializers.CurrentUserDefault()
    )

    class Meta:
        # fields = ('id', 'text', 'author', 'score', 'pub_date')
        fields = '__all__'
        read_only_fields = ('title',)
        model = Review

        '''
        validators = [
            UniqueTogetherValidator(
                queryset=Review.objects.all(),
                fields=('user', 'title'),
                message='Юзер уже подписан на автора!'
            )
        ]
        '''

class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        read_only=True, slug_field='username'
    )

    class Meta:
        fields = ('id', 'text', 'author', 'pub_date')
        model = Comment
