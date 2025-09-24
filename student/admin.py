from django.contrib import admin
from .models import Student, Department



from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin


class StudentInline(admin.TabularInline):
    model = Student



CustomUser = get_user_model()
@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    inlines = [StudentInline]


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    search_fields = ['student_id__username', 'first_name', 'department']
    fields = (('first_name', 'last_name'), ('student_id', 'department'))
    list_display = ('first_name', 'last_name', 'student_id', 'department')
    list_display_links = ('first_name', 'student_id')
    list_filter = ('department__name',)
    list_per_page = 30

admin.site.register(Department)