from django.contrib import admin
from .models import Contact, Group, Template, Message, Draft

# Register the Contact model
@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone_number', 'user')
    search_fields = ('name', 'phone_number', 'user__username')
    list_filter = ('user',)

# Register the Group model
@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'description')
    search_fields = ('name', 'description', 'user__username')
    list_filter = ('user',)
    filter_horizontal = ('contacts',)  # Easier selection for many-to-many fields

# Register the Template model
@admin.register(Template)
class TemplateAdmin(admin.ModelAdmin):
    list_display = ('title', 'user')
    search_fields = ('title', 'content', 'user__username')
    list_filter = ('user',)

# Register the Message model
@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('content', 'user', 'status', 'timestamp', 'schedule_time')
    search_fields = ('content', 'user__username', 'status')
    list_filter = ('status', 'timestamp', 'user')
    filter_horizontal = ('recipients', 'group_recipients')  # Easier selection for many-to-many fields
    date_hierarchy = 'timestamp'

# Register the Draft model
@admin.register(Draft)
class DraftAdmin(admin.ModelAdmin):
    list_display = ('content', 'user', 'timestamp')
    search_fields = ('content', 'user__username')
    list_filter = ('timestamp', 'user')
    filter_horizontal = ('recipients', 'group_recipients')  # Easier selection for many-to-many fields
