from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import Sentence, PronunciationResult, Client, Profile, Word, Term

# Inline admin to include Profile in the User admin
class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Profile'
    fk_name = 'user'

# Custom UserAdmin that includes Profile inline
class UserAdmin(BaseUserAdmin):
    inlines = (ProfileInline,)

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2'),
        }),
    )

    def get_inline_instances(self, request, obj=None):
        if not obj:
            return []
        return super().get_inline_instances(request, obj)

# Re-register the User model with the new UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)

# Existing model admin registrations
admin.site.register(Sentence)
admin.site.register(PronunciationResult)
admin.site.register(Word)

@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'client', 'is_admin')
    list_filter = ('client', 'is_admin')

@admin.register(Term)
class TermAdmin(admin.ModelAdmin):
    list_display = ('term', 'position', 'client', 'user', 'created_at')
    list_filter = ('client',)
    search_fields = ('term',)
    ordering = ('client', 'position')