from django.contrib import admin

from .models import Category, Comment, Genre, GenreTitle, Review, Title, User


class UserAdmin(admin.ModelAdmin):
    list_display = (
        "username",
        "role",
        "email",
        "first_name",
        "last_name",
        "bio",
    )


class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}


class GenreAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}


class TitleAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "year",
        "description",
        "category",
        "get_genre",
    )


class GenreTitleAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "genre")


class ReviewAdmin(admin.ModelAdmin):
    list_display = ("author", "title", "text", "score", "pub_date")


class CommentAdmin(admin.ModelAdmin):
    list_display = ("author", "review", "text", "pub_date")


admin.site.register(User, UserAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Genre, GenreAdmin)
admin.site.register(Title, TitleAdmin)
admin.site.register(GenreTitle, GenreTitleAdmin)
admin.site.register(Review, ReviewAdmin)
admin.site.register(Comment, CommentAdmin)
