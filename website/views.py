from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .forms import SignUpForm, SMSMessageForm, ContactForm, ContactListForm, ContactFilterForm, SentMessagesFilterForm
from django.contrib.auth.decorators import login_required
from .models import SMSMessage, Contact, ContactList, SentMessage
import datetime

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
                # messages.success(request, "You have successfully logged in.")
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
    # messages.success(request, "You have successfully logged out.")
    return redirect('home')

# compose sms
@login_required
def compose(request):
    if request.method == 'POST':
        form = SMSMessageForm(request.POST)
        if form.is_valid():
            # Save the SMSMessage instance but don't commit yet
            sms_message = form.save(commit=False)
            sms_message.user = request.user  # Associate the SMS message with the current user
            sms_message.save()

            # Save the sent message details to the SentMessage model
            SentMessage.objects.create(
                sender=sms_message.from_number,
                recipients=sms_message.to,  # Assuming 'to' contains a single recipient or a comma-separated list
                message=sms_message.message,
                user=request.user,
                status="Pending" if sms_message.scheduled_date else "Sent",  # Handle scheduling status
            )

            # (Optional) Schedule or send the SMS
            # You can use a task scheduler like Celery for background processing
            # Example: if sms_message.scheduled_date, schedule the SMS using Celery

            return redirect('sms_dashboard')  # Redirect to the dashboard or success page
    else:
        form = SMSMessageForm()

    return render(request, 'compose.html', {'form': form})


@login_required
def contacts(request):
    if request.method == 'POST':
        form = SMSMessageForm(request.POST)
        if form.is_valid():
            # Save the form, but with custom modifications for 'from_number' and 'scheduled_date'
            sms_message = form.save(commit=False)
            sms_message.user = request.user  # Associate the SMS message with the current user
            sms_message.save()

            # Schedule or send SMS if necessary
            # (You can use Celery or other task schedulers here)
            return redirect('sms_dashboard')  # Redirect to a dashboard or success page
    else:
        form = SMSMessageForm()

    return render(request, 'contacts.html', {'form': form})

@login_required
def personalize(request):
    if request.method == 'POST':
        form = SMSMessageForm(request.POST)
        if form.is_valid():
            # Save the form, but with custom modifications for 'from_number' and 'scheduled_date'
            sms_message = form.save(commit=False)
            sms_message.user = request.user  # Associate the SMS message with the current user
            sms_message.save()

            # Schedule or send SMS if necessary
            # (You can use Celery or other task schedulers here)
            return redirect('sms_dashboard')  # Redirect to a dashboard or success page
    else:
        form = SMSMessageForm()

    return render(request, 'personalize.html', {'form': form})


# View for listing contacts
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
def sent(request):
    form = SentMessagesFilterForm(request.GET or None)
    messages = SMSMessage.objects.all()

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
