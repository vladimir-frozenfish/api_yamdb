import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models

from .validators import validate_year

SCORE = (
    (1, 1),
    (2, 2),
    (3, 3),
    (4, 4),
    (5, 5),
    (6, 6),
    (7, 7),
    (8, 8),
    (9, 9),
    (10, 10),
)


class UserRoles:
    ADMIN = 'admin'
    MODERATOR = 'moderator'
    USER = 'user'


class User(AbstractUser):
    role_user = (
        (UserRoles.USER, UserRoles.USER),
        (UserRoles.MODERATOR, UserRoles.MODERATOR),
        (UserRoles.ADMIN, UserRoles.ADMIN),
    )
    username = models.CharField(max_length=150,
                                unique=True)
    role = models.CharField(max_length=16,
                            choices=role_user, default="user")
    bio = models.TextField(blank=True,
                           null=True)
    first_name = models.CharField(max_length=150,
                                  blank=True, null=True)
    last_name = models.CharField(max_length=150,
                                 blank=True, null=True)
    email = models.EmailField(max_length=254, unique=True)
    confirmation_code = models.CharField(max_length=50,
                                         blank=True)

    @property
    def is_admin(self):
        return (self.is_staff or self.role == UserRoles.ADMIN
                or self.is_superuser)

    @property
    def is_moderator(self):
        return self.role == UserRoles.MODERATOR or self.is_superuser

    def save(self, *args, **kwargs):
        if self.confirmation_code == "":
            self.confirmation_code = uuid.uuid3(uuid.NAMESPACE_DNS,
                                                self.email)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.username

    class Meta:
        ordering = ["id"]


class Category(models.Model):
    name = models.CharField(max_length=256, verbose_name="Категория")
    slug = models.SlugField(
        max_length=50, unique=True, verbose_name="URL_categorie"
    )

    class Meta:
        verbose_name_plural = "Категории"
        verbose_name = "Категория"

    def __str__(self):
        return self.name


class Genre(models.Model):
    name = models.CharField(max_length=256, verbose_name="Жанр")
    slug = models.SlugField(
        max_length=50, unique=True, verbose_name="URL_genre"
    )

    class Meta:
        verbose_name_plural = "Жанры"
        verbose_name = "Жанр"

    def __str__(self):
        return self.name


class Title(models.Model):
    name = models.CharField(max_length=256, verbose_name="Имя_произведения")
    year = models.IntegerField(validators=[validate_year],
                               verbose_name="Год_создания_произведения")
    description = models.TextField(verbose_name="Описание_произведения")
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="titles",
        verbose_name="Категория_произведения",
    )
    genre = models.ManyToManyField(Genre, through="GenreTitle")

    def get_genre(self):
        return ", ".join([genre.name for genre in self.genre.all()])

    get_genre.short_description = "Жанры произведения"

    class Meta:
        verbose_name_plural = "Произведения"
        verbose_name = "Произведение"

    def __str__(self):
        return self.name


class GenreTitle(models.Model):
    genre = models.ForeignKey(Genre, on_delete=models.CASCADE)
    title = models.ForeignKey(Title, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.genre} {self.title}"


class Review(models.Model):
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="reviews"
    )
    title = models.ForeignKey(
        Title, on_delete=models.CASCADE, related_name="reviews"
    )
    text = models.TextField()
    score = models.IntegerField(choices=SCORE)
    pub_date = models.DateTimeField(
        "Дата добавления", auto_now_add=True, db_index=True
    )

    class Meta:
        verbose_name_plural = "Отзывы"
        verbose_name = "Отзыв"

        constraints = [
            models.UniqueConstraint(
                fields=["author", "title"], name="unique_user_review"
            )
        ]

    def __str__(self):
        return self.text[:20]


class Comment(models.Model):
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="comments"
    )
    review = models.ForeignKey(
        Review, on_delete=models.CASCADE, related_name="comments"
    )
    text = models.TextField()
    pub_date = models.DateTimeField(
        "Дата добавления", auto_now_add=True, db_index=True
    )

    class Meta:
        verbose_name_plural = "Комментарии к отзывам"
        verbose_name = "Комментарий к отзыву"

    def __str__(self):
        return self.text[:20]
