from django.contrib import admin

# Register your models here.
from .models import UserNodeProgress, SessionCompletion, UserStreakState

admin.site.register(UserNodeProgress)

@admin.register(SessionCompletion) # Using the decorator to register the model with a custom admin class. This allows us to customize the admin interface for SessionCompletion.
class SessionCompletionAdmin(admin.ModelAdmin):
    list_display = ("user", "calendar_date", "completed_at") # Displaying the user, calendar date and completion time in the admin list view for easy reference.
    filter_horizontal = ("reinforcement_nodes",) # Using a horizontal filter widget for the many-to-many relationship with reinforcement nodes, which provides a more user-friendly interface for selecting multiple nodes.
    

@admin.register(UserStreakState)
class UserStreakStateAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "streak",
        "freeze_streak",
        "consecutive_zero_session_days",
        "last_evaluated_date",
        "updated_at",
    )
    readonly_fields = ("updated_at",)