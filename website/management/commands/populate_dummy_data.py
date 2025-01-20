from django.core.management.base import BaseCommand
from website.models import User, Contact, Group, Message, Draft, Template
from django.utils.timezone import now

class Command(BaseCommand):
    help = 'Populate the database with dummy data for testing'

    def handle(self, *args, **kwargs):
        # Create 10 dummy users with unique usernames
        users = []
        for i in range(1, 11):
            # Create unique usernames like user1, user2, ..., user10
            username = f"user{i}_username"
            user = User.objects.create_user(username=username, password="password123")
            users.append(user)

        # Create dummy contacts for each user
        for user in users:
            contact1 = Contact.objects.create(user=user, name=f"Contact1 {user.username}", phone_number=f"12345{user.id}")
            contact2 = Contact.objects.create(user=user, name=f"Contact2 {user.username}", phone_number=f"12345{user.id + 1}")
            contact3 = Contact.objects.create(user=user, name=f"Contact3 {user.username}", phone_number=f"12345{user.id + 2}")
            
            # Ensure contacts are used by adding them to groups and drafts
            # Create dummy groups for each user
            group1 = Group.objects.create(user=user, name=f"Group1 {user.username}")
            group1.contacts.add(contact1, contact2)  # Add first two contacts to group
            
            group2 = Group.objects.create(user=user, name=f"Group2 {user.username}")
            group2.contacts.add(contact2, contact3)  # Add last two contacts to group

            # Create dummy messages for each user
            Message.objects.create(user=user, content="Hello, this is a test message", status="draft", timestamp=now())
            Message.objects.create(user=user, content="Scheduled message", status="scheduled", schedule_time=now(), timestamp=now())
            Message.objects.create(user=user, content="Test sent message", status="sent", timestamp=now())

            # Create dummy drafts for each user
            for i in range(1, 4):  # Create 3 drafts per user
                draft = Draft.objects.create(user=user, content=f"Draft message {i} for {user.username}", timestamp=now())
                draft.recipients.add(contact1, contact2)  # Add first two contacts to draft

            # Create dummy templates for each user
            for i in range(1, 4):  # Create 3 templates per user
                Template.objects.create(user=user, title=f"Template {i} for {user.username}", content=f"Template message {i} for {user.username}")

        self.stdout.write(self.style.SUCCESS('Successfully populated the database with dummy data'))
