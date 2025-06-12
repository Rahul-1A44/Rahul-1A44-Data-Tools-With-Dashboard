from django.contrib import admin
from .models import Project, DataAnalysis

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'created_at')
    list_filter = ('user', 'created_at')
    search_fields = ('name', 'description')

@admin.register(DataAnalysis)
class DataAnalysisAdmin(admin.ModelAdmin):
    list_display = ('title', 'project', 'created_at')
    list_filter = ('project', 'created_at')
    search_fields = ('title',)