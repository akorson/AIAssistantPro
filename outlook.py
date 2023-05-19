import requests
from datetime import datetime, timedelta
from msal import PublicClientApplication
from google.cloud import translate
from googleapiclient.discovery import build
from google.oauth2 import service_account
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders
import base64
import os
import csv
from openpyxl import Workbook
import datetime as dt


def route_emails(emails):
    cookcounty_domain = "cookcounty.il.gov"
    cookcounty_email_recipients = ["department@example.com", "manager@example.com"]
    order_keywords = ["order", "orders"]
    order_email_recipients = ["orders@example.com", "sales@example.com"]
    urgent_keywords = ["emergency", "urgent", "immediate", "compliance"]
    urgent_email_recipients = ["urgent@example.com", "manager@example.com"]
    billing_keywords = ["billing", "invoices", "payment"]
    billing_email_recipients = ["billing@example.com"]

    routed_emails = []

    for email in emails:
        sender_email = email.get('sender', '').lower()
        subject = email.get('subject', '').lower()
        body = email.get('body', '').lower()

        if cookcounty_domain in sender_email:
            email['recipients'] = cookcounty_email_recipients
            routed_emails.append(email)
        elif any(keyword in subject or keyword in body for keyword in order_keywords):
            email['recipients'] = order_email_recipients
            routed_emails.append(email)
        elif any(keyword in subject or keyword in body for keyword in urgent_keywords):
            email['recipients'] = urgent_email_recipients
            routed_emails.append(email)
        elif any(keyword in subject or keyword in body for keyword in billing_keywords):
            email['recipients'] = billing_email_recipients
            routed_emails.append(email)

    return routed_emails


def generate_email_template(template_data):
    subject = template_data.get('subject')
    recipient_name = template_data.get('recipient_name')
    email_body = template_data.get('email_body')

    email_template = f"Dear {recipient_name},\n\n"
    email_template += email_body + "\n\n"
    email_template += "Sincerely,\nYour Name"

    return email_template


def send_text_message_via_zapier(message, recipient_phone_number):
    zapier_webhook_url = 'https://hooks.zapier.com/hooks/catch/1234567/abcdefg'
    payload = {
        'message': message,
        'phone_number': recipient_phone_number
    }
    response = requests.post(zapier_webhook_url, json=payload)
    if response.status_code == 200:
        return True
    else:
        return False


def send_teams_message_reminder(message, recipient_email, access_token):
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    payload = {
        'to': {
            'emailAddress': {
                'address': recipient_email
            }
        },
        'message': {
            'body': {
                'content': message
            }
        }
    }
    response = requests.post('https://graph.microsoft.com/v1.0/me/chats', headers=headers, json=payload)
    if response.status_code == 201:
        return True
    else:
        return False


def create_calendar_event_reminder(subject, message, start_datetime, end_datetime, recipient_email, access_token):
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    event = {
        'subject': subject,
        'body': {
            'contentType': 'Text',
            'content': message
        },
        'start': {
            'dateTime': start_datetime,
            'timeZone': 'UTC'
        },
        'end': {
            'dateTime': end_datetime,
            'timeZone': 'UTC'
        },
        'attendees': [
            {
                'emailAddress': {
                    'address': recipient_email
                },
                'type': 'required'
            }
        ]
    }
    response = requests.post('https://graph.microsoft.com/v1.0/me/events', headers=headers, json=event)
    created_event = response.json()
    return created_event.get('id')


def create_daily_event_reminder(subject, message, recipient_email, access_token):
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    today = datetime.today().date()
    tomorrow = today + timedelta(days=1)
    start_datetime = f'{tomorrow}T09:00:00'
    end_datetime = f'{tomorrow}T10:00:00'
    event = {
        'subject': subject,
        'body': {
            'contentType': 'Text',
            'content': message
        },
        'start': {
            'dateTime': start_datetime,
            'timeZone': 'UTC'
        },
        'end': {
            'dateTime': end_datetime,
            'timeZone': 'UTC'
        },
        'attendees': [
            {
                'emailAddress': {
                    'address': recipient_email
                },
                'type': 'required'
            }
        ]
    }
    response = requests.post('https://graph.microsoft.com/v1.0/me/events', headers=headers, json=event)
    created_event = response.json()
    return created_event.get('id')


def get_outlook_emails(access_token):
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    response = requests.get('https://graph.microsoft.com/v1.0/me/messages', headers=headers)
    emails = response.json().get('value', [])
    return emails


def authenticate_with_graph_api(client_id, client_secret, tenant_id):
    scopes = ['https://graph.microsoft.com/.default']
    app = PublicClientApplication(client_id=client_id, authority=f'https://login.microsoftonline.com/{tenant_id}')
    token = app.acquire_token_for_client(scopes=scopes, client_secret=client_secret)
    return token['access_token']


def translate_text(text, target_language):
    translate_client = translate.TranslationServiceClient()
    parent = translate_client.location_path('your-project-id', 'global')
    response = translate_client.translate_text(
        request={
            "parent": parent,
            "contents": [text],
            "mime_type": "text/plain",
            "target_language_code": target_language,
        }
    )
    translated_text = response.translations[0].translated_text
    return translated_text


def generate_google_drive_file_preview(file_id, preview_width, preview_height, credentials_path):
    credentials = service_account.Credentials.from_service_account_file(credentials_path, scopes=["https://www.googleapis.com/auth/drive"])
    service = build('drive', 'v3', credentials=credentials)
    thumbnail = service.files().get(fileId=file_id, fields='thumbnailLink').execute()
    thumbnail_url = thumbnail.get('thumbnailLink')
    preview_url = f"{thumbnail_url}=w{preview_width}-h{preview_height}"
    return preview_url


def create_google_meet_event(summary, start_datetime, end_datetime, meeting_link, credentials_path):
    credentials = service_account.Credentials.from_service_account_file(credentials_path, scopes=["https://www.googleapis.com/auth/calendar.events"])
    service = build('calendar', 'v3', credentials=credentials)
    event = {
        'summary': summary,
        'start': {'dateTime': start_datetime},
        'end': {'dateTime': end_datetime},
        'conferenceData': {
            'createRequest': {
                'requestId': 'random-string',
                'conferenceSolutionKey': {
                    'type': 'hangoutsMeet'
                }
            }
        },
        'attendees': [
            {'email': 'participant1@example.com'},
            {'email': 'participant2@example.com'}
        ]
    }
    if meeting_link:
        event['conferenceData']['entryPoints'] = [{'entryPointType': 'video', 'uri': meeting_link}]
    created_event = service.events().insert(calendarId='primary', body=event).execute()
    return created_event.get('id')


def send_email_with_attachments(sender_email, receiver_email, subject, message, attachments, credentials_path):
    credentials = service_account.Credentials.from_service_account_file(credentials_path, scopes=["https://www.googleapis.com/auth/gmail.send"])
    service = build('gmail', 'v1', credentials=credentials)

    email_message = MIMEMultipart()
    email_message['From'] = sender_email
    email_message['To'] = receiver_email
    email_message['Subject'] = subject
    email_message.attach(MIMEText(message, 'plain'))

    for attachment_path in attachments:
        attachment_name = os.path.basename(attachment_path)
        with open(attachment_path, 'rb') as attachment:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(attachment.read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', f'attachment; filename= {attachment_name}')
            email_message.attach(part)

    raw_message = base64.urlsafe_b64encode(email_message.as_bytes()).decode()
    sent_message = service.users().messages().send(userId='me', body={'raw': raw_message}).execute()

    return sent_message.get('id')


def get_google_calendar_event(event_id, credentials_path):
    credentials = service_account.Credentials.from_service_account_file(credentials_path, scopes=["https://www.googleapis.com/auth/calendar"])
    service = build('calendar', 'v3', credentials=credentials)
    event = service.events().get(calendarId='primary', eventId=event_id).execute()
    return event


def create_google_sheets_chart(spreadsheet_id, chart_title, data_range, chart_type, credentials_path):
    credentials = service_account.Credentials.from_service_account_file(credentials_path, scopes=["https://www.googleapis.com/auth/spreadsheets"])
    service = build('sheets', 'v4', credentials=credentials)
    chart_spec = {
        'title': chart_title,
        'basicChart': {
            'chartType': chart_type,
            'legendPosition': 'BOTTOM_LEGEND',
            'axis': [
                {'position': 'BOTTOM_AXIS', 'title': 'X-axis'},
                {'position': 'LEFT_AXIS', 'title': 'Y-axis'}
            ],
            'domains': [
                {'domain': {'sourceRange': {'sources': [{'sheetId': 0, 'startRowIndex': data_range[0], 'endRowIndex': data_range[1], 'startColumnIndex': 0, 'endColumnIndex': 1}]}}}
            ],
            'series': [
                {'series': {'sourceRange': {'sources': [{'sheetId': 0, 'startRowIndex': data_range[0], 'endRowIndex': data_range[1], 'startColumnIndex': 1, 'endColumnIndex': 2}]}}}
            ]
        }
    }
    chart_request = {
        'addChart': {
            'chart': chart_spec,
            'position': {
                'newSheet': True
            }
        }
    }
    request = service.spreadsheets().batchUpdate(spreadsheetId=spreadsheet_id, body={'requests': [chart_request]})
    response = request.execute()
    chart_id = response['replies'][0]['addChart']['chart']['chartId']
    return chart_id


def export_google_sheets_data(spreadsheet_id, range_name, export_format, export_path, credentials_path):
    credentials = service_account.Credentials.from_service_account_file(credentials_path, scopes=["https://www.googleapis.com/auth/spreadsheets"])
    service = build('sheets', 'v4', credentials=credentials)
    request = service.spreadsheets().values().get(spreadsheetId=spreadsheet_id, range=range_name)
    response = request.execute()
    values = response.get('values', [])

    if values:
        with open(export_path, 'w', newline='') as file:
            writer = csv.writer(file)
            if export_format == 'csv':
                writer.writerows(values)
            elif export_format == 'excel':
                workbook = Workbook()
                worksheet = workbook.active
                for row in values:
                    worksheet.append(row)
                workbook.save(export_path)
        return True
    return False


def create_google_drive_shortcut(file_id, target_folder_id, credentials_path):
    credentials = service_account.Credentials.from_service_account_file(credentials_path, scopes=["https://www.googleapis.com/auth/drive"])
    service = build('drive', 'v3', credentials=credentials)
    shortcut_metadata = {
        'name': 'Shortcut',
        'mimeType': 'application/vnd.google-apps.shortcut',
        'shortcutDetails': {
            'targetId': file_id,
            'targetMimeType': 'application/vnd.google-apps.file'
        },
        'parents': [target_folder_id]
    }
    shortcut = service.files().create(body=shortcut_metadata).execute()
    return shortcut.get('id')


def rename_google_drive_file(file_id, new_name, credentials_path):
    credentials = service_account.Credentials.from_service_account_file(credentials_path, scopes=["https://www.googleapis.com/auth/drive"])
    service = build('drive', 'v3', credentials=credentials)
    file_metadata = {'name': new_name}
    renamed_file = service.files().update(fileId=file_id, body=file_metadata).execute()
    return renamed_file.get('id')


def copy_google_drive_file(file_id, credentials_path):
    credentials = service_account.Credentials.from_service_account_file(credentials_path, scopes=["https://www.googleapis.com/auth/drive"])
    service = build('drive', 'v3', credentials=credentials)
    copied_file = service.files().copy(fileId=file_id).execute()
    return copied_file.get('id')


def search_google_scholar_publications(query, credentials_path):
    credentials = service_account.Credentials.from_service_account_file(credentials_path, scopes=["https://www.googleapis.com/auth/scholar"])
    service = build('scholar', 'v1', credentials=credentials)
    response = service.publications().search(query=query).execute()
    publications = response.get('publications', [])
    return publications


def send_html_email_with_gmail(sender_email, receiver_email, subject, message_html, credentials_path):
    credentials = service_account.Credentials.from_service_account_file(credentials_path, scopes=["https://www.googleapis.com/auth/gmail.send"])
    service = build('gmail', 'v1', credentials=credentials)

    email_message = f"From: {sender_email}\nTo: {receiver_email}\nSubject: {subject}\nContent-Type: text/html; charset=utf-8\n\n{message_html}"
    encoded_message = base64.urlsafe_b64encode(email_message.encode()).decode()
    sent_message = service.users().messages().send(userId='me', body={'raw': encoded_message}).execute()

    return sent_message.get('id')


def update_google_calendar_event(event_id, updated_event, credentials_path):
    credentials = service_account.Credentials.from_service_account_file(credentials_path, scopes=["https://www.googleapis.com/auth/calendar"])
    service = build('calendar', 'v3', credentials=credentials)
    event = service.events().update(calendarId='primary', eventId=event_id, body=updated_event).execute()
    return event


def delete_google_calendar_event(event_id, credentials_path):
    credentials = service_account.Credentials.from_service_account_file(credentials_path, scopes=["https://www.googleapis.com/auth/calendar"])
    service = build('calendar', 'v3', credentials=credentials)
    service.events().delete(calendarId='primary', eventId=event_id).execute()


def list_google_calendar_events(credentials_path):
    credentials = service_account.Credentials.from_service_account_file(credentials_path, scopes=["https://www.googleapis.com/auth/calendar"])
    service = build('calendar', 'v3', credentials=credentials)
    now = dt.datetime.utcnow().isoformat() + 'Z'
    events = service.events().list(calendarId='primary', timeMin=now, orderBy='startTime').execute()
    event_list = events.get('items', [])
    return event_list


def move_google_drive_file(file_id, new_folder_id, credentials_path):
    credentials = service_account.Credentials.from_service_account_file(credentials_path, scopes=["https://www.googleapis.com/auth/drive"])
    service = build('drive', 'v3', credentials=credentials)
    file = service.files().get(fileId=file_id, fields='parents').execute()
    previous_parents = ",".join(file.get('parents'))
    file = service.files().update(fileId=file_id, addParents=new_folder_id, removeParents=previous_parents, fields='id, parents').execute()
    return file


def share_google_drive_file(file_id, email_addresses, permissions, credentials_path):
    credentials = service_account.Credentials.from_service_account_file(credentials_path, scopes=["https://www.googleapis.com/auth/drive"])
    service = build('drive', 'v3', credentials=credentials)

    permission_list = []
    for email, permission in zip(email_addresses, permissions):
        permission_list.append({
            'type': 'user',
            'role': permission,
            'emailAddress': email
        })

    batch = service.new_batch_http_request()
    for permission in permission_list:
        batch.add(service.permissions().create(fileId=file_id, body=permission))

    batch.execute()


def delete_google_drive_file(file_id, credentials_path):
    credentials = service_account.Credentials.from_service_account_file(credentials_path, scopes=["https://www.googleapis.com/auth/drive"])
    service = build('drive', 'v3', credentials=credentials)
    service.files().delete(fileId=file_id).execute()


def get_google_drive_file_metadata(file_id, credentials_path):
    credentials = service_account.Credentials.from_service_account_file(credentials_path, scopes=["https://www.googleapis.com/auth/drive"])
    service = build('drive', 'v3', credentials=credentials)
    file = service.files().get(fileId=file_id, fields='name, size, modifiedTime').execute()
    return file


def create_google_calendar_event(summary, start_datetime, end_datetime, credentials_path):
    credentials = service_account.Credentials.from_service_account_file(credentials_path, scopes=["https://www.googleapis.com/auth/calendar.events"])
    service = build('calendar', 'v3', credentials=credentials)
    event = {
        'summary': summary,
        'start': {'dateTime': start_datetime},
        'end': {'dateTime': end_datetime}
    }
    created_event = service.events().insert(calendarId='primary', body=event).execute()
    return created_event.get('id')
