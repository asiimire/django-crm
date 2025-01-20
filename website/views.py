from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.conf import settings
from .forms import (
    PersonalizeMessageForm,
    SignUpForm,
    MessageForm,
    ContactForm,
    ContactFilterForm,
    SentMessagesFilterForm,
    TemplateForm,
)
from .models import Draft, Group, Message, Contact, Template
from dcrm.utils.sms_service import sms_service
import pandas as pd

import logging
logger = logging.getLogger(__name__)



def home(request):
    login_form_data = {'username': '', 'password': ''}
    register_form = SignUpForm()

    if request.method == "POST":
        if 'login' in request.POST:
            username, password = request.POST.get('username'), request.POST.get('password')
            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                return redirect('compose')
            else:
                messages.error(request, "Invalid username or password.")
                login_form_data = {'username': username, 'password': ''}

        elif 'register' in request.POST:
            register_form = SignUpForm(request.POST)
            if register_form.is_valid():
                user = register_form.save(commit=False)
                user.set_password(register_form.cleaned_data['password1'])
                user.save()
                login(request, user)
                messages.success(request, "Account created successfully. Welcome!")
                return redirect('compose')
            messages.error(request, "Please fix the errors in the registration form.")

    return render(request, 'home.html', {'login_form_data': login_form_data, 'register_form': register_form})


def logout_user(request):
    logout(request)
    return redirect('home')


@login_required
def compose(request):
    # user_credits = Transaction.objects.filter(
    #     user=request.user, status="Completed"
    # ).aggregate(total_credits=Sum("amount"))["total_credits"] or 0

    draft_id = request.GET.get("draft_id")
    sms_message = get_object_or_404(Message, id=draft_id, user=request.user, status="draft") if draft_id else None
    form = MessageForm(instance=sms_message)

    if request.method == "POST":
        form = MessageForm(request.POST, instance=sms_message)
        if form.is_valid():
            sms_message = form.save(commit=False)
            sms_message.user = request.user

            if "save_draft" in request.POST:
                sms_message.status = "draft"
                sms_message.save()
                messages.success(request, "Draft saved successfully!")
                return redirect("drafts_list")

            sms_message.status = "pending"
            sms_message.save()

            try:
                sms_service.send(
                    message=form.cleaned_data['message'],
                    recipients=form.cleaned_data['recipients'].split(",")
                )
                sms_message.status = "sent"
                sms_message.save()
                messages.success(request, "Messages sent successfully!")
            except Exception as e:
                logger.error(f"SMS sending failed: {e}")
                messages.error(request, f"Failed to send messages: {e}")


            return redirect("draft_list")

    return render(request, "compose.html", {
        "form": form,
        "username": request.user.username,
        # "credits": user_credits,
        "groups": Group.objects.filter(user=request.user),
    })


@login_required
def drafts_list(request):
    drafts = Message.objects.filter(user=request.user, status="draft").order_by('-timestamp')
    return render(request, 'drafts.html', {'drafts': drafts})


@login_required
def delete_draft(request, draft_id):
    draft = get_object_or_404(Message, id=draft_id, user=request.user, status="draft")
    draft.delete()
    messages.success(request, "Draft deleted successfully.")
    return redirect('drafts_list')


@login_required
def edit_draft(request, draft_id):
    draft = get_object_or_404(Message, id=draft_id, user=request.user, status="draft")
    form = PersonalizeMessageForm(request.POST or None, instance=draft)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Draft updated successfully.")
        return redirect('drafts_list')
    return render(request, 'edit_draft.html', {'form': form})


# @login_required
# def top_up(request):
#     form = TopUpForm(request.POST or None)
#     if request.method == "POST" and form.is_valid():
#         transaction = Transaction.objects.create(
#             user=request.user,
#             amount=form.cleaned_data["amount"],
#             phone_number=form.cleaned_data["phone_number"],
#             status="Pending",
#         )
#         return HttpResponse(f"Payment initiated for {transaction.phone_number}!")
#     recent_transactions = Transaction.objects.filter(user=request.user).order_by("-date")[:5]
#     return render(request, "top_up.html", {"form": form, "recent_transactions": recent_transactions})


@login_required
def personalize(request):
    form = PersonalizeMessageForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        try:
            uploaded_file = request.FILES['upload_file']
            data = pd.read_csv(uploaded_file) if uploaded_file.name.endswith('.csv') else pd.read_excel(uploaded_file)

            if 'name' not in data.columns:
                messages.error(request, "The file must have a 'name' column.")
                return redirect('personalize')

            for _, row in data.iterrows():
                personalized_message = form.cleaned_data['message'].replace('@@name@@', row['name'])
                print(f"Sending to {row['name']}: {personalized_message}")  # Replace with actual SMS API logic

            messages.success(request, "Messages sent successfully!")
        except Exception as e:
            messages.error(request, f"Error processing file: {e}")

    return render(request, 'personalize.html', {'form': form})

@login_required
def contacts(request):
    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            # Save the form, but with custom modifications for 'from_number' and 'scheduled_date'
            sms_message = form.save(commit=False)
            sms_message.user = request.user  # Associate the SMS message with the current user
            sms_message.save()

            # Schedule or send SMS if necessary
            # (You can use Celery or other task schedulers here)
            return redirect('sms_dashboard')  # Redirect to a dashboard or success page
    else:
        form = MessageForm()

    return render(request, 'contacts.html', {'form': form})

# View for listing contacts
@login_required
def contact_list(request):
    form = ContactFilterForm(request.GET)
    contacts = Contact.objects.filter(user=request.user)  # Filter by the logged-in user

    if form.is_valid():
        search_query = form.cleaned_data.get('search_query')
        if search_query:
            contacts = contacts.filter(name__icontains=search_query)

        contact_type = form.cleaned_data.get('contact_type')
        if contact_type:
            contacts = contacts.filter(contact_type=contact_type)

        page_size = form.cleaned_data.get('page_size')
        if page_size:
            contacts = contacts[:int(page_size)]

    return render(request, 'contacts.html', {'form': form, 'contacts': contacts})

# View for creating a new contact
@login_required
def create_contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('contact_list')
    else:
        form = ContactForm()

    return render(request, 'create_contact.html', {'form': form})

# sent messages
@login_required
def sent(request):
    form = SentMessagesFilterForm(request.GET or None)
    messages = Message.objects.all()

    # Filter based on form data
    if form.is_valid():
        keyword = form.cleaned_data.get('keyword')
        type_filter = form.cleaned_data.get('type')
        date_from = form.cleaned_data.get('date_from')
        date_to = form.cleaned_data.get('date_to')

        if keyword:
            messages = messages.filter(message__icontains=keyword)
        if type_filter and type_filter != 'any':
            messages = messages.filter(repeat=type_filter)
        if date_from:
            messages = messages.filter(scheduled_date__gte=date_from)
        if date_to:
            messages = messages.filter(scheduled_date__lte=date_to)

    context = {
        'form': form,
        'messages': messages,
    }
    return render(request, 'sent.html', context)

# template messages
@login_required
def template(request):
    templates = Template.objects.filter(user=request.user)  # Filter by the logged-in user
    if request.method == 'POST':
        form = TemplateForm(request.POST)
        if form.is_valid():
            # Process the form data
            template_name = form.cleaned_data['template_name']
            message = form.cleaned_data['message']
            # Save or process the data as needed
            Template.objects.create(user=request.user, title=template_name, content=message)
            messages.success(request, "Template created successfully!")
            return redirect('template')  # Redirect to avoid resubmission
    else:
        form = TemplateForm()

    return render(request, 'template.html', {'form': form, 'templates': templates})
