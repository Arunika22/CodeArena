from django.contrib import admin
from .models import Problem, TestCase, Contest, Submission, Leaderboard

class TestCaseInline(admin.TabularInline):
    model = TestCase
    extra = 1

class ProblemAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'created_at')
    search_fields = ('title', 'description')
    list_filter = ('created_at',)
    ordering = ('-created_at',)
    inlines = [TestCaseInline]

class TestCaseAdmin(admin.ModelAdmin):
    list_display = ('id', 'problem', 'input_data', 'output_data', 'is_sample')
    search_fields = ('problem__title', 'input_data')
    list_filter = ('is_sample',)
    ordering = ('-problem',)

class ContestAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'start_time', 'end_time')
    search_fields = ('name',)
    list_filter = ('start_time', 'end_time')
    ordering = ('-start_time',)

class SubmissionAdmin(admin.ModelAdmin):
    list_display = ('id', 'problem', 'temporary_username', 'status', 'submitted_at')
    search_fields = ('temporary_username', 'problem__title')
    list_filter = ('status', 'submitted_at')
    ordering = ('-submitted_at',)

class LeaderboardAdmin(admin.ModelAdmin):
    list_display = ('contest', 'temporary_username', 'total_score')
    search_fields = ('temporary_username', 'contest__name')
    ordering = ('-total_score',)

admin.site.register(Problem, ProblemAdmin)
admin.site.register(TestCase, TestCaseAdmin)
admin.site.register(Contest, ContestAdmin)
admin.site.register(Submission, SubmissionAdmin)
admin.site.register(Leaderboard, LeaderboardAdmin)
