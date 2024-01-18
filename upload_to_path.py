from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import mimetypes
import os

def authenticate_drive():
    # Set the path to your credentials JSON file
    credentials_path = 'credentials.json'

    creds = service_account.Credentials.from_service_account_file(
        credentials_path,
        scopes=['https://www.googleapis.com/auth/drive']
    )
    drive_service = build('drive', 'v3', credentials=creds)
    return drive_service

def get_or_create_folder(service, parent_folder_id, folder_path):
    # Split the folder path into individual folder names
    folder_names = folder_path.split('/')

    current_parent_id = parent_folder_id

    for folder_name in folder_names:
        # Check if the folder exists
        folder_id = get_folder_id(service, current_parent_id, folder_name)

        if not folder_id:
            # If the folder doesn't exist, create it
            folder_metadata = {
                'name': folder_name,
                'mimeType': 'application/vnd.google-apps.folder',
                'parents': [current_parent_id] if current_parent_id else None
            }

            folder = service.files().create(
                body=folder_metadata,
                fields='id'
            ).execute()

            print(f'Folder "{folder_name}" created in folder with ID {current_parent_id}. Folder ID: {folder["id"]}')
            current_parent_id = folder['id']
        else:
            # If the folder exists, use its ID
            current_parent_id = folder_id

    return current_parent_id

def get_folder_id(service, parent_id, folder_name):
    # Search for the folder by name within the specified parent
    folders = service.files().list(
        q=f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false and '{parent_id}' in parents",
        spaces='drive',
        fields='files(id)').execute().get('files', [])

    if folders:
        return folders[0]['id']
    else:
        return None


def share_file_with_emails(service, file_id, email_addresses):
    # Set the permission for each email address (Read access in this case)
    for email_address in email_addresses:
        permission = {
            'type': 'user',
            'role': 'reader',
            'emailAddress': email_address
        }

        # Create the permission
        service.permissions().create(
            fileId=file_id,
            body=permission,
            fields='id'
        ).execute()

        print(f'File shared with {email_address}')



def upload_file(service, file_path, folder_id, share_with_emails, share=False):
    # Set the file name and MIME type
    file_name = file_path.split("/")[-1]
    mimetype, _ = mimetypes.guess_type(file_path)

    # Set the metadata for the file
    file_metadata = {
        'name': file_name,
        'parents': [folder_id] if folder_id else None
    }

    # Create a MediaFileUpload object and upload the file
    media = MediaFileUpload(file_path, mimetype=mimetype)
    uploaded_file = service.files().create(
        body=file_metadata,
        media_body=media,
        fields='id'
    ).execute()

    print(f'File uploaded to folder with ID {folder_id}. File ID: {uploaded_file["id"]}')
    # Delete the local file after successful upload
    # Share the file with a specific email address
    uploaded_file_id = uploaded_file["id"]
    if share:
        print("sharing file with the owner/s")
        share_file_with_emails(service, uploaded_file_id, share_with_emails)

    os.remove(file_path)

    print(f'Local file deleted: {file_path}')

if __name__ == '__main__':
    # Replace 'path/to/your/credentials.json' with the actual path to your downloaded credentials JSON file
    drive_service = authenticate_drive()

    # Replace 'your_parent_folder_id' with the ID of the Google Drive folder where you want to create the new folder
    parent_folder_id = 'your_parent_folder_id'

    # Replace 'New/Folder/Path' with the desired path for the new folder
    new_folder_path = 'New/Folder/Path'

    # Replace 'path/to/your/file.txt' with the actual path to the file you want to upload
    file_to_upload = 'path/to/your/file.txt'

    # Get or create the folder
    new_folder_id = get_or_create_folder(drive_service, parent_folder_id, new_folder_path)

    # Upload the file to the newly created or existing folder
    upload_file(drive_service, file_to_upload, new_folder_id)
