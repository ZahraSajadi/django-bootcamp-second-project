from django.contrib import admin
from .models import Comment, Rating, Reservation, Room


class CommentInlineAdmin(admin.TabularInline):
    model = Comment
    show_change_link = True
    extra = 1


class RatingInlineAdmin(admin.TabularInline):
    model = Rating
    extra = 1
    show_change_link = True


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ("name", "capacity", "status")
    list_filter = ("status",)
    search_fields = ("description__icontains",)
    inlines = [CommentInlineAdmin, RatingInlineAdmin]


@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ("room", "user", "team")
    list_filter = ("room", "user", "team", "date")


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("user", "room", "created_at", "short_content")
    list_filter = ("user", "room", "created_at")
    search_fields = ("content",)

    def short_content(self, obj: Comment):
        short_content = obj.content
        if len(short_content) > 30:
            short_content = short_content[:30] + "..."
        return short_content


@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display = ("user", "room", "value")
    list_filter = ("user", "room")
