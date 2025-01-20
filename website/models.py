from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now

# Contact model for storing individual user contacts
class Contact(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="contacts")
    name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=15)

    def __str__(self):
        return f"{self.name} ({self.phone_number})"

# Group model for organizing contacts into groups
class Group(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="contact_groups")
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    contacts = models.ManyToManyField(Contact, related_name="groups")

    def __str__(self):
        return f"{self.name} (by {self.user.username})"

# Template model for storing reusable message templates
class Template(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="templates")
    title = models.CharField(max_length=100)
    content = models.TextField()

    def __str__(self):
        return f"Template: {self.title} (by {self.user.username})"

# Message model for storing messages (sent or drafts)
class Message(models.Model):
    STATUS_CHOICES = [
        ("sent", "Sent"),
        ("draft", "Draft"),
        ("scheduled", "Scheduled"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="messages")  # Existing user field
    content = models.TextField()  # Existing message content
    sender_id = models.CharField(max_length=100)  # New sender_id field
    message = models.TextField()  # New message field (can be the same as content if needed)
    recipients = models.ManyToManyField(Contact, related_name="messages")
    group_recipients = models.ManyToManyField(Group, related_name="messages", blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="draft")
    timestamp = models.DateTimeField(default=now)
    schedule_time = models.DateTimeField(blank=True, null=True)

    def save(self, *args, **kwargs):
        # Set sender_id as the user's name before saving
        self.sender_id = self.user.username  # This stores the sender's name as a string
        self.message = self.content  # Set message field as content
        super(Message, self).save(*args, **kwargs)

    def __str__(self):
        return f"Message by {self.user.username} ({self.get_status_display()})"

    class Meta:
        ordering = ["-timestamp"]

        
# Draft model to specifically save drafts separately if needed
class Draft(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="drafts")
    content = models.TextField()
    timestamp = models.DateTimeField(default=now)
    recipients = models.ManyToManyField(Contact, related_name="drafts", blank=True)
    group_recipients = models.ManyToManyField(Group, related_name="drafts", blank=True)

    def __str__(self):
        return f"Draft by {self.user.username} ({self.timestamp.strftime('%Y-%m-%d %H:%M')})"
