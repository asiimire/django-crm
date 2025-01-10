from django.db import models
from django.contrib.auth.models import User

class SMSMessage(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    to = models.CharField(max_length=255)
    from_number = models.CharField(max_length=255)
    message = models.TextField()
    scheduled_date = models.DateTimeField(null=True, blank=True)
    repeat = models.CharField(max_length=50, choices=[('none', 'None'), ('daily', 'Daily'), ('weekly', 'Weekly')], default='none')
    sent = models.BooleanField(default=False)

    def __str__(self):
        return f"Message to {self.to} by {self.user.username}"

class Contact(models.Model):
    name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=15, unique=True)
    email = models.EmailField(blank=True, null=True)
    group = models.CharField(max_length=255, blank=True, null=True)  # Optional: to group contacts
    status = models.BooleanField(default=True)  # Active (True) or Inactive (False)
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

# ContactList model
class ContactList(models.Model):
    name = models.CharField(max_length=255)
    contacts = models.ManyToManyField(Contact, related_name='lists')
    is_private = models.BooleanField(default=True)
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

# sent messages
class SentMessage(models.Model):
    sender = models.CharField(max_length=255)  # Sender ID (e.g., 'NMF')
    recipients = models.TextField()  # Store a list of recipient numbers as a comma-separated string
    message = models.TextField()  # The actual message sent
    date_sent = models.DateTimeField(auto_now_add=True)  # Auto-set when the message is sent
    status = models.CharField(max_length=50, default="Sent")  # Status of the message (e.g., Sent, Failed)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)  # User who sent the message

    def __str__(self):
        return f"Message from {self.sender} to {self.recipients[:20]} ({self.status})"