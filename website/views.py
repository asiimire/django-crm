from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .forms import (
    PersonalizeMessageForm,
    SignUpForm,
    MessageForm,
    ContactForm,
    ContactListForm,
    ContactFilterForm,
    SentMessagesFilterForm
)
from django.contrib.auth.decorators import login_required
from .models import Group, Message, Contact, Transaction
import datetime
from django.db.models import Sum



def home(request):
    # Initialize forms
    login_form_data = {'username': '', 'password': ''}
    register_form = SignUpForm()

    if request.method == "POST":
        if 'login' in request.POST:  # Login form submitted
            username = request.POST.get('username')
            password = request.POST.get('password')
            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                return redirect('compose')  # Redirect to the compose page
            else:
                messages.error(request, "Invalid username or password.")
                login_form_data = {'username': username, 'password': ''}  # Retain username in form

        elif 'register' in request.POST:  # Registration form submitted
            register_form = SignUpForm(request.POST)
            if register_form.is_valid():
                register_form.save()
                username = register_form.cleaned_data['username']
                password = register_form.cleaned_data['password1']
                user = authenticate(request, username=username, password=password)
                if user:
                    login(request, user)
                    messages.success(request, "Account created successfully. Welcome!")
                    return redirect('compose')  # Redirect to the compose page
            else:
                messages.error(request, "Please fix the errors in the registration form.")

    context = {
        'login_form_data': login_form_data,
        'register_form': register_form,
    }
    return render(request, 'home.html', context)


# logout user
def logout_user(request):
    logout(request)
    return redirect('home')


# compose sms
@login_required
def compose(request):
    user_credits = Transaction.objects.filter(
        user=request.user, status="Completed"
    ).aggregate(total_credits=Sum("amount"))["total_credits"] or 0

    # Check if loading a draft
    draft_id = request.GET.get("draft_id")
    if draft_id:
        sms_message = get_object_or_404(Message, id=draft_id, user=request.user)
        form = MessageForm(instance=sms_message)
    else:
        sms_message = None
        form = MessageForm()

    if request.method == "POST":
        form = MessageForm(request.POST, instance=sms_message)
        if form.is_valid():
            sms_message = form.save(commit=False)
            sms_message.user = request.user

            # Check if the user clicked "Save as Draft"
            if "save_draft" in request.POST:
                sms_message.status = "draft"
                sms_message.save()
                return redirect("drafts")  # Redirect to drafts page

            # Default for a message to be sent
            sms_message.status = "pending"
            sms_message.save()

            # Placeholder: Add logic for sending SMS
            return redirect("compose")

    # Fetch user-created groups for the phonebook dropdown
    groups = Group.objects.filter(user=request.user)

    context = {
        "form": form,
        "username": request.user.username,
        "credits": user_credits,
        "groups": groups,  # Pass groups to the template
    }

    return render(request, "compose.html", context)

@login_required
def drafts(request):
    drafts = Message.objects.filter(user=request.user, status="draft")
    return render(request, "drafts.html", {"drafts": drafts})

@login_required
def delete_draft(request, id):
    draft = get_object_or_404(Message, id=id, user=request.user, status="draft")
    draft.delete()
    return redirect("drafts")



@login_required
def top_up(request):
    if request.method == "POST":
        form = TopUpForm(request.POST)
        if form.is_valid():
            transaction = Transaction.objects.create(
                user=request.user,  # Associate the transaction with the logged-in user
                amount=form.cleaned_data["amount"],
                phone_number=form.cleaned_data["phone_number"],
                status="Pending",
            )
            return HttpResponse(f"Payment initiated for {transaction.phone_number}!")
    else:
        form = TopUpForm()

    recent_transactions = Transaction.objects.filter(user=request.user).order_by("-date")[:5]

    return render(request, "top_up.html", {"form": form, "recent_transactions": recent_transactions})


# View for contacts and other views remain unchanged

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

@login_required
def personalize(request):
    if request.method == 'POST':
        form = PersonalizeMessageForm(request.POST)
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

    return render(request, 'personalize.html', {'form': form})


# View for listing contacts
@login_required
def contact_list(request):
    form = ContactFilterForm(request.GET)
    contacts = Contact.objects.all()

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


# View for creating a new contact list
@login_required
def create_contact_list(request):
    if request.method == 'POST':
        form = ContactListForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('contacts')
    else:
        form = ContactListForm()

    return render(request, 'create_contact_list.html', {'form': form})

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
# @login_required
# def template(request):
#     if request.method == 'POST':
#         form = TemplateForm(request.POST)
#         if form.is_valid():
#             # Process the form data
#             template_name = form.cleaned_data['template_name']
#             message = form.cleaned_data['message']
#             # Save or process the data as needed
#             print(f"Template Name: {template_name}, Message: {message}")
#             return redirect('template')  # Redirect to avoid resubmission
#     else:
#         form = TemplateForm()

#     return render(request, 'template.html', {'form': form})