from django.contrib import admin
from .models import Group, Message, Contact, ContactList, SentMessage, Template, Transaction


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'user')
    search_fields = ('name', 'user__username')
    list_filter = ('user',)


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('sender_id', 'status', 'send_later_time', 'group')
    search_fields = ('sender_id', 'recipients', 'message')
    list_filter = ('status', 'send_later_time')
    autocomplete_fields = ('group',)


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone_number', 'group', 'status', 'date_added')
    search_fields = ('name', 'phone_number', 'email')
    list_filter = ('status', 'date_added')
    ordering = ('-date_added',)


@admin.register(ContactList)
class ContactListAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_private', 'date_created')
    search_fields = ('name',)
    list_filter = ('is_private', 'date_created')
    filter_horizontal = ('contacts',)


@admin.register(SentMessage)
class SentMessageAdmin(admin.ModelAdmin):
    list_display = ('sender', 'recipients', 'status', 'date_sent', 'user')
    search_fields = ('sender', 'recipients')
    list_filter = ('status', 'date_sent')
    autocomplete_fields = ('user',)


@admin.register(Template)
class TemplateAdmin(admin.ModelAdmin):
    list_display = ('name', 'last_modified')
    search_fields = ('name', 'message')
    list_filter = ('last_modified',)
    ordering = ('-last_modified',)


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('user', 'sms_count', 'amount', 'phone_number', 'status', 'date')
    search_fields = ('user__username', 'phone_number')
    list_filter = ('status', 'date')
    ordering = ('-date',)
