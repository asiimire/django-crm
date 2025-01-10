from django.contrib import admin
from .models import SMSMessage, Contact, ContactList

class SMSMessageAdmin(admin.ModelAdmin):
    list_display = ('user', 'to', 'from_number', 'scheduled_date', 'sent')
    list_filter = ('repeat', 'sent', 'scheduled_date')
    search_fields = ('to', 'from_number', 'message')

class ContactAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone_number', 'email', 'status', 'date_added')
    list_filter = ('status', 'date_added')
    search_fields = ('name', 'phone_number', 'email')

class ContactListAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_private', 'date_created')
    list_filter = ('is_private', 'date_created')
    search_fields = ('name',)

# Registering the models with custom admin classes
admin.site.register(SMSMessage, SMSMessageAdmin)
admin.site.register(Contact, ContactAdmin)
admin.site.register(ContactList, ContactListAdmin)
