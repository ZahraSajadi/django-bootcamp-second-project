from django.contrib import admin
from .models import Comment, Rating, Reservation, Room


class CommentInlineAdmin(admin.TabularInline):
    model = Comment
    show_change_link = True
    extra = 1


class RatingInlineAdmin(admin.TabularInline):
    model = Rating
    show_change_link = True
    extra = 1


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ("name", "capacity", "is_active")
    list_filter = ("is_active",)
    search_fields = (
        "name__icontains",
        "description__icontains",
    )
    inlines = [CommentInlineAdmin, RatingInlineAdmin]


@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ("room", "reserver_user", "team", "start_date", "end_date")
    list_filter = ("room", "reserver_user", "team", "start_date", "end_date")


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("user", "room", "created_at", "short_content")
    list_filter = ("user", "room", "created_at")
    search_fields = ("content__icontains",)

    def short_content(self, obj: Comment):
        short_content = obj.content
        if len(short_content) > 30:
            short_content = short_content[:30] + "..."
        return short_content


@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display = ("user", "room", "value")
    list_filter = ("user", "room")
