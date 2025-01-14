from django.db import models
from django.contrib.auth.models import User

class Group(models.Model):
    name = models.CharField(max_length=255)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='custom_groups')  # Change 'groups' to 'custom_groups'

    def __str__(self):
        return self.name

class Message(models.Model):
    STATUS_CHOICES = [('draft', 'Draft'), ('sent', 'Sent')]
    sender_id = models.CharField(max_length=11)
    recipients = models.TextField()
    message = models.TextField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')
    send_later_time = models.DateTimeField(null=True, blank=True)
    group = models.ForeignKey(Group, null=True, blank=True, on_delete=models.SET_NULL)

    def __str__(self):
        return f"{self.sender_id} - {self.status}"

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

    
class Template(models.Model):
    name = models.CharField(max_length=255)
    message = models.TextField()
    last_modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

# payment

class Transaction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    sms_count = models.IntegerField(null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    phone_number = models.CharField(max_length=15)
    date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, default="Pending")

    def __str__(self):
        return f"{self.phone_number} - {self.amount} UGX"
