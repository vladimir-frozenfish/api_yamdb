from api_yamdb.settings import SERVICE_EMAIL
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response
from reviews.models import Comment, Review, Title, User

from .serializers import CommentSerializer, ReviewSerializer, UserSerializer


@api_view(['POST'])
def send_register_code(request):
    username = request.data.get('username')
    email = request.data.get('email')
    data = {'username': username,
            'email': email}
    serializer = UserSerializer(data=data)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    confirmation_code = User.objects.get(username=username).confirmation_code
    send_mail(
        'Служба технического сопровождения YAMDB services',
        f'Привет! Держи свой код доступа {confirmation_code}.',
        SERVICE_EMAIL,
        [email],
        fail_silently=False
        
    )
    return Response(data, status=status.HTTP_200_OK)


@api_view(['POST'])
def get_jwt_token(request):
    
    pass


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer

    def get_queryset(self):
        title_id = self.kwargs.get("title_id")
        title = get_object_or_404(Title, id=title_id)
        new_queryset = title.reviews.all()
        return new_queryset


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer

    def get_queryset(self):
        review_id = self.kwargs.get("review_id")
        review = get_object_or_404(Review, id=review_id)
        new_queryset = review.comments.all()
        return new_queryset
