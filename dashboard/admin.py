# from django.contrib import admin
# from .models import Problem

# # Customize the admin interface for the Problem model
# class ProblemAdmin(admin.ModelAdmin):
#     list_display = ('id', 'title', 'created_at')
#     search_fields = ('title', 'description')
#     list_filter = ('created_at',)
#     ordering = ('-created_at',)

# # Register the Problem model with the custom admin interface
# admin.site.register(Problem, ProblemAdmin)
from django.contrib import admin
from .models import Contest, Problem, Submission, Leaderboard

# Customize the admin interface for the Problem model
class ProblemAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'created_at')
    search_fields = ('title', 'description')
    list_filter = ('created_at',)
    ordering = ('-created_at',)

# Customize the admin interface for the Contest model
class ContestAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'start_time', 'end_time')
    search_fields = ('name',)
    list_filter = ('start_time', 'end_time')
    ordering = ('-start_time',)

# Customize the admin interface for the Submission model
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ('id', 'problem', 'temporary_username', 'status', 'submitted_at')
    search_fields = ('temporary_username', 'problem__title')
    list_filter = ('status', 'submitted_at')
    ordering = ('-submitted_at',)

# Customize the admin interface for the Leaderboard model
class LeaderboardAdmin(admin.ModelAdmin):
    list_display = ('contest', 'temporary_username', 'total_score')
    search_fields = ('temporary_username', 'contest__name')
    ordering = ('-total_score',)

# Register all models with their custom admin interfaces
admin.site.register(Problem, ProblemAdmin)
admin.site.register(Contest, ContestAdmin)
admin.site.register(Submission, SubmissionAdmin)
admin.site.register(Leaderboard, LeaderboardAdmin)
