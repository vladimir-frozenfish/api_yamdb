import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models

score = (
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


class User(AbstractUser):
    role_user = (
        ("user", "user"),
        ("moderator", "moderator"),
        ("admin", "admin"),
    )
    role = models.CharField(max_length=16, choices=role_user, default="user")
    bio = models.TextField(
        "Биография",
        blank=True,
    )
    email = models.EmailField(
        max_length=254, unique=True, blank=False, null=False
    )

    confirmation_code = models.CharField(
        max_length=50,
        blank=True,
    )

    @property
    def is_admin(self):
        return self.is_staff or self.role == "admin" or self.is_superuser

    @property
    def is_moderator(self):
        return self.role == "moderator" or self.is_superuser

    def save(self, *args, **kwargs):
        if self.confirmation_code == "":
            self.confirmation_code = uuid.uuid3(uuid.NAMESPACE_DNS, self.email)
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
    year = models.IntegerField(verbose_name="Год_создания_произведения")
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
    score = models.IntegerField(choices=score)
    pub_date = models.DateTimeField(
        "Дата добавления", auto_now_add=True, db_index=True
    )

    class Meta:
        verbose_name_plural = "Отзывы"
        verbose_name = "Отзыв"

        constraints = [
            models.UniqueConstraint(
                fields=["author", "title"], name="unique_user_following"
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
