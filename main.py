import csv
import upload_to_path
import getAccessToken
import lucidSession

with open('metadata.csv', 'r') as csv_file:
    reader_obj = csv.DictReader(csv_file)
    access_token = getAccessToken.get_lucid_access_token()
    drive_service = upload_to_path.authenticate_drive()
    for row in reader_obj:
        documentId = row['Document ID']
        filename = documentId + '.jpeg'
        if row['Deletion status'] != 'In Trash':
            response = lucidSession.get_document(documentId, access_token)
            if not response.ok:
                print("Something did not go well")
                print(response)
                # print(row['Document URL'])
            else:
                with open(filename, 'wb') as outfile:
                    print("saving file to google drive")
                    outfile.write(response.content)
                    parent_folder_id = '1BCo_4Lt7r1lfV0E83RfJhcMFu-2ha36n'
                    folder_id = upload_to_path.get_or_create_folder(drive_service, parent_folder_id, row['Owner'])
                    upload_to_path.upload_file(drive_service, filename, folder_id, str.split(row['Internal users']+row['External users'], ','))
