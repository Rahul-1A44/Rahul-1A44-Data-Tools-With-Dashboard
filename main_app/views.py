from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from .forms import RegistrationForm
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from .tokens import account_activation_token
from django.core.mail import EmailMessage
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.http import HttpResponse, FileResponse, HttpResponseBadRequest
from django.utils import timezone
from datetime import timedelta
from django.conf import settings
from .forms import CustomAuthenticationForm
from django.core.files.storage import FileSystemStorage
import os

import json
import csv
import io
import pandas as pd


from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from io import BytesIO
from reportlab.lib.utils import simpleSplit

from .services.scraper import scrape_website
from .services.converter import convert_data
from .services.analysis import perform_auto_analysis
from django.contrib.auth.decorators import login_required


def index(request):
    """
    Renders the main index page, passing any existing messages.
    """
    return render(request, 'index.html', {})


def dashboard(request):
    """
    Renders the user dashboard page.
    """
    # No message for unauthenticated users on dashboard access
    return render(request, 'dashboard.html')


def data_analysis(request):
    """
    Handles automatic data analysis requests. Processes uploaded data, performs auto-analysis,
    and displays results including tables and charts.
    """
    analysis_results = None
    analysis_error = None
    uploaded_file_name = None
    df_html_table = None

    if request.method == 'POST':
        if not request.user.is_authenticated:
            # Removed: messages.warning(request, "Please log in to perform data analysis.")
            analysis_error = "Login required to perform analysis. Please log in or register."
        else:
            if 'data_file' in request.FILES:
                uploaded_file = request.FILES['data_file']
                uploaded_file_name = uploaded_file.name
                file_extension = uploaded_file_name.split('.')[-1].lower()
                file_content = uploaded_file.read()

                analysis_output = perform_auto_analysis(file_content, file_extension)

                if 'error' in analysis_output:
                    analysis_error = analysis_output['error']
                    messages.error(request, f"Analysis failed: {analysis_error}")
                else:
                    analysis_results = analysis_output['results']

                    try:
                        if file_extension == 'csv':
                            try:
                                df = pd.read_csv(io.StringIO(file_content.decode('utf-8')))
                            except UnicodeDecodeError:
                                df = pd.read_csv(io.StringIO(file_content.decode('latin1')))
                        elif file_extension == 'xlsx':
                            df = pd.read_excel(io.BytesIO(file_content))
                        elif file_extension == 'json':
                            df = pd.read_json(io.StringIO(file_content.decode('utf-8')))
                        else:
                            raise ValueError("Unsupported file type for raw data display.")

                        df.dropna(axis=1, how='all', inplace=True)

                        df_html_table = df.head(1000).to_html(classes='table table-dark table-striped table-bordered dataframe table-responsive')

                    except Exception as e:
                        print(f"Warning: Error preparing raw data table for display: {e}")


            else:
                analysis_error = "Please upload a data file to perform analysis."
                messages.error(request, analysis_error)

    context = {
        'analysis_results': analysis_results,
        'analysis_error': analysis_error,
        'uploaded_file_name': uploaded_file_name,
        'df_html_table': df_html_table,
    }
    return render(request, 'data/data_analysis.html', context)


def data_converter(request):
    """
    Handles data conversion requests. Processes input data (text or file upload),
    converts it between specified formats (e.g., JSON, YAML, Text, PDF, XLSX, CSV),
    and displays the results directly or provides download links for binary files.
    """
    converted_data_display = None
    download_link = None
    conversion_error = None
    input_data_retained = ""
    selected_input_format = "text"
    selected_output_format = "json"
    input_file_present = False

    if request.method == 'POST':
        selected_input_format = request.POST.get('input_format', 'text')
        selected_output_format = request.POST.get('output_format', 'json')

        input_content = None

        if not request.user.is_authenticated:
            # Removed: messages.warning(request, "Please log in to perform data conversion.")
            conversion_error = "Login required to perform conversion. Please log in or register."
        else:
            if 'input_file' in request.FILES:
                input_file_present = True
                uploaded_file = request.FILES['input_file']
                input_content = uploaded_file.read()
            else:
                input_data_retained = request.POST.get('input_data', '')
                input_content = input_data_retained

            if not input_content or (isinstance(input_content, str) and not input_content.strip()):
                messages.error(request, "Input data or file cannot be empty. Please provide data or upload a file to convert.")
                conversion_error = "Please provide data or upload a file to convert."
            else:
                result = convert_data(input_content, selected_input_format, selected_output_format)

                if 'error' in result:
                    conversion_error = result['error']
                    messages.error(request, f"Conversion failed: {conversion_error}")
                else:
                    converted_output = result['converted_data']
                    is_binary = result.get('is_binary', False)

                    if is_binary:
                        fs = FileSystemStorage(location=settings.MEDIA_ROOT)
                        file_extension = selected_output_format
                        filename = f"converted_file_{timezone.now().strftime('%Y%m%d%H%M%S')}.{file_extension}"
                        file_path = fs.path(filename)

                        os.makedirs(os.path.dirname(file_path), exist_ok=True)

                        with open(file_path, 'wb') as f:
                            f.write(converted_output)

                        download_link = fs.url(filename)
                    else:
                        converted_data_display = converted_output

    context = {
        'input_data': input_data_retained,
        'input_format': selected_input_format,
        'output_format': selected_output_format,
        'converted_data_display': converted_data_display,
        'conversion_error': conversion_error,
        'download_link': download_link,
        'input_file_present': input_file_present,
    }
    return render(request, 'data/data_converter.html', context)


def data_scraping(request):
    """
    Handles web scraping requests, processing user input for target URL, scraping type,
    and desired output format. It scrapes data, formats it, and provides options for
    display and download.
    """
    scraped_data_display = None
    download_link = None
    scrape_error = None


    target_url = ''
    scraping_type_selected = 'all_text'
    output_scrape_format = 'json'
    custom_selector = ''

    if request.method == 'POST':
        target_url = request.POST.get('target_url', '')
        scraping_type_selected = request.POST.get('scraping_type', 'all_text')
        output_scrape_format = request.POST.get('output_scrape_format', 'json')
        custom_selector = request.POST.get('custom_selector', '')

        if not request.user.is_authenticated:
            # Removed: messages.warning(request, "Please log in to perform web scraping.")
            scrape_error = "Login required to perform scraping. Please log in or register."
        else:
            if not target_url:
                scrape_error = "Please provide a target URL to start scraping."
                messages.warning(request, scrape_error)
            else:

                raw_scraped_data = scrape_website(target_url, scraping_type_selected, custom_selector)

                if 'error' in raw_scraped_data:
                    scrape_error = raw_scraped_data['error']
                    messages.error(request, f"Scraping failed: {scrape_error}")
                elif not raw_scraped_data.get('data'):
                    scrape_error = "No data was scraped for the selected criteria."
                    messages.info(request, scrape_error)
                else:

                    request.session['raw_scraped_data_for_download'] = raw_scraped_data['data']
                    request.session['scraped_output_format'] = output_scrape_format

                    is_binary_output = False

                    try:

                        if output_scrape_format == 'json':
                            scraped_data_display = json.dumps(raw_scraped_data['data'], indent=2)
                        elif output_scrape_format == 'csv':

                            if isinstance(raw_scraped_data['data'], list) and all(isinstance(item, dict) for item in raw_scraped_data['data']):
                                df = pd.DataFrame(raw_scraped_data['data'])
                            elif isinstance(raw_scraped_data['data'], dict):
                                df = pd.DataFrame([raw_scraped_data['data']])
                            else:

                                df = pd.DataFrame([{'content': str(raw_scraped_data['data'])}])

                            output_buffer = io.StringIO()
                            df.to_csv(output_buffer, index=False)
                            scraped_data_display = output_buffer.getvalue()
                        elif output_scrape_format == 'text':

                            text_output = ""
                            if isinstance(raw_scraped_data['data'], list):
                                for item in raw_scraped_data['data']:
                                    if isinstance(item, dict):
                                        for k, v in item.items():
                                            text_output += f"{k}: {v}\n"
                                    else:
                                        text_output += f"{item}\n"
                                    text_output += "---\n"
                            elif isinstance(raw_scraped_data['data'], dict):
                                for k, v in raw_scraped_data['data'].items():
                                    text_output += f"{k}: {v}\n"
                            else:
                                text_output = str(raw_scraped_data['data'])
                            scraped_data_display = text_output.strip()
                        elif output_scrape_format == 'pdf':
                            is_binary_output = True
                            scraped_data_display = f"Click 'Download Scraped File' to get the PDF."
                        elif output_scrape_format == 'xlsx':
                            is_binary_output = True
                            scraped_data_display = f"Click 'Download Scraped File' to get the XLSX."
                        else:
                            scrape_error = "Unsupported output format selected."
                            messages.error(request, f"Unsupported output format: {output_scrape_format}.")
                            scraped_data_display = None

                        if not scrape_error:

                            download_link = f"/download-scraped-data/?format={output_scrape_format}"

                    except Exception as e:
                        scrape_error = f"Error formatting scraped data for display/download: {e}"
                        messages.error(request, f"Error preparing display/download: {e}")
                        scraped_data_display = None

    context = {
        'target_url': target_url,
        'scraping_type': scraping_type_selected,
        'custom_selector': custom_selector,
        'output_scrape_format': output_scrape_format,
        'scraped_data_display': scraped_data_display,
        'download_link': download_link,
        'scrape_error': scrape_error,
    }
    return render(request, 'data/data_scraping.html', context)


@login_required(redirect_field_name=None)
def download_scraped_data(request):
    """
    View to handle downloading the scraped data stored in the session.
    The data is retrieved from session, formatted, and served as a file.
    This view requires login as it relies on session data set by the data_scraping view
    after a successful scraping operation (which now requires login).
    """
    raw_scraped_data = request.session.pop('raw_scraped_data_for_download', None)
    output_format = request.session.pop('scraped_output_format', 'json')

    if raw_scraped_data is None:
        messages.error(request, "No scraped data found for download. Please perform a new scrape (login required).")
        return HttpResponseBadRequest("No scraped data found for download. Please perform a new scrape.")

    try:
        if output_format == 'json':
            response = HttpResponse(json.dumps(raw_scraped_data, indent=2), content_type='application/json')
            response['Content-Disposition'] = 'attachment; filename="scraped_data.json"'
        elif output_format == 'csv':
            output_buffer = io.StringIO()

            if isinstance(raw_scraped_data, list) and all(isinstance(item, dict) for item in raw_scraped_data):
                df = pd.DataFrame(raw_scraped_data)
            elif isinstance(raw_scraped_data, dict):
                df = pd.DataFrame([raw_scraped_data])
            else:
                df = pd.DataFrame([{'content': str(raw_scraped_data)}])

            df.to_csv(output_buffer, index=False)
            response = HttpResponse(output_buffer.getvalue(), content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="scraped_data.csv"'
        elif output_format == 'text':
            text_output = ""
            if isinstance(raw_scraped_data, list):
                for item in raw_scraped_data:
                    if isinstance(item, dict):
                        for k, v in item.items():
                            text_output += f"{k}: {v}\n"
                    else:
                        text_output += f"{item}\n"
                    text_output += "---\n"
            elif isinstance(raw_scraped_data, dict):
                for k, v in raw_scraped_data.items():
                    text_output += f"{k}: {v}\n"
            else:
                text_output = str(raw_scraped_data)

            response = HttpResponse(text_output, content_type='text/plain')
            response['Content-Disposition'] = 'attachment; filename="scraped_data.txt"'
        elif output_format == 'pdf':
            buffer = BytesIO()
            p = canvas.Canvas(buffer, pagesize=letter)

            text_content = ""
            if isinstance(raw_scraped_data, (list, dict)):
                text_content = json.dumps(raw_scraped_data, indent=2)
            else:
                text_content = str(raw_scraped_data)


            left_margin = 50
            right_margin = 50
            top_start_y = 750
            bottom_margin = 50
            page_width, page_height = letter
            available_width = page_width - left_margin - right_margin

            font_name = 'Helvetica'
            font_size = 10
            line_height = font_size + 2

            p.setFont(font_name, font_size)

            current_y = top_start_y

            all_lines = text_content.split('\n')

            for original_line in all_lines:

                wrapped_sub_lines = simpleSplit(original_line, font_name, font_size, available_width)


                if not wrapped_sub_lines:
                    wrapped_sub_lines = [""]

                for sub_line in wrapped_sub_lines:


                    if current_y < bottom_margin:
                        p.showPage()
                        p.setFont(font_name, font_size)

                        current_y = top_start_y

                    p.drawString(left_margin, current_y, sub_line)
                    current_y -= line_height

            p.save()
            converted_data = buffer.getvalue()
            buffer.close()

            response = HttpResponse(converted_data, content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; filename="scraped_data.pdf"'

        elif output_format == 'xlsx':
            output_buffer = BytesIO()

            df = None
            if isinstance(raw_scraped_data, list):
                if all(isinstance(i, dict) for i in raw_scraped_data):
                    df = pd.DataFrame(raw_scraped_data)
                elif all(isinstance(i, str) for i in raw_scraped_data):
                    df = pd.DataFrame(raw_scraped_data, columns=['content'])
                else:
                    df = pd.DataFrame([{'content': str(item)} for item in raw_scraped_data])
            elif isinstance(raw_scraped_data, dict):
                df = pd.DataFrame([raw_scraped_data])
            else:
                df = pd.DataFrame(str(raw_scraped_data).splitlines(), columns=['content'])

            if df is not None:
                df.to_excel(output_buffer, index=False, engine='openpyxl')
                converted_data = output_buffer.getvalue()
                output_buffer.close()

                response = HttpResponse(converted_data, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
                response['Content-Disposition'] = 'attachment; filename="scraped_data.xlsx"'
            else:
                return HttpResponseBadRequest("Failed to convert data to Excel format.")
        else:
            return HttpResponseBadRequest("Unsupported download format.")

        return response

    except Exception as e:
        print(f"Error during download: {e}")
        return HttpResponseBadRequest(f"Error preparing file for download: {e}")


def projects(request):
    """
    Renders the projects page.
    """
    # No message for unauthenticated users on projects access
    return render(request, 'projects.html')


def user_login(request):
    """
    Handles user login using a custom authentication form.
    Redirects to the dashboard upon successful login.
    """
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)

            return redirect('dashboard')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field.replace("_", " ").title()}: {error}')
    else:
        form = CustomAuthenticationForm()
    return render(request, 'login.html', {'form': form})


@login_required(redirect_field_name=None)
def user_logout(request):
    """
    Logs out the current user and redirects them to the login page.
    Requires login to execute logout.
    """
    logout(request)

    return redirect('login')


def register_user(request):
    """
    Handles user registration, including sending an activation email.
    New users are marked as inactive until their email is confirmed.
    """
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            try:
                user = form.save(commit=False)
                user.is_active = False
                user.save()

                current_site = get_current_site(request)
                mail_subject = 'Activate your account'
                message = render_to_string('account_activation_email.html', {
                    'user': user,
                    'domain': current_site.domain,
                    'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                    'token': account_activation_token.make_token(user),
                    'protocol': 'https' if request.is_secure() else 'http'
                })

                to_email = form.cleaned_data.get('email')
                email = EmailMessage(
                    mail_subject,
                    message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    to=[to_email]
                )
                email.send(fail_silently=False)


                return redirect('login')

            except Exception as e:
                if user and user.pk:
                    user.delete()
                messages.error(request, f'Registration failed. Please try again. Error: {str(e)}')
                return redirect('register_user')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field.replace("_", " ").title()}: {error}')
    else:
        form = RegistrationForm()

    return render(request, 'register.html', {'form': form})


def activate(request, uidb64, token):
    """
    Activates a user account using a unique ID and token from an email link.
    Logs the user in upon successful activation.
    """
    User = get_user_model()
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        # Check if the token is too old (e.g., more than 24 hours, adjust timedelta as needed)
        # Note: 'user.date_joined' is not the creation time of the token. A better approach
        # for token expiration would involve storing a timestamp with the token or using a more robust
        # token generation mechanism if strict expiration is needed beyond Django's default token lifespan.
        # For this example, I'll use a simple check against user.date_joined which acts as a rough
        # proxy, assuming activation happens shortly after registration.
        token_expiration_time = timezone.now() - timedelta(days=1) # Token valid for 24 hours
        if user.date_joined < token_expiration_time and not user.is_active:
            messages.error(request, 'Activation link has expired. Please register again.')
            return redirect('register_user')

        user.is_active = True
        user.save()
        login(request, user)

        return redirect('dashboard')
    else:
        messages.error(request, 'Activation link is invalid or has already been used.')
        return redirect('dashboard')


@login_required(redirect_field_name=None)
def profile(request):
    """
    Renders the user profile page.
    Requires login to view the profile.
    """
    return render(request, 'profile.html')