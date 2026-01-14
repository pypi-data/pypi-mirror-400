from .authorization import authorize
from urllib import parse
import requests
import json

# Global API variables
files_endpoint = '/api/v1/files'
folders_endpoint = '/api/v1/folder'
files_folder_get = '/get'
files_getstream = '/getfilestream'
files_getDmsId = '/getbydmsid'
files_folder_create = '/create'
files_folder_update = '/update'
files_folder_archive = '/archive'
files_folder_delete = '/delete'
folder_getByPath = '/getfolderbypath'
folder_getOrCreateByPath = '/getorcreatefolderbypath'
folder_getChildren = '/getchildfolders'
folder_getFiles = '/getfiles'
default_headers = {'accept': 'application/json',
                   'user-agent': 'govAccess/Implementation'}
image_types = ['gif', 'png', 'jpg', 'jpe', 'jpeg', 'tiff', 'tif', 'bmp', 'ico', 'svg']
media_types = ['asf', ' asx', ' wm', ' wmx', ' wmp', ' wma', ' wax', ' wmv', ' wvx', ' avi', ' wav', ' mpeg',
               ' mpg', ' mpe', ' mov', ' m1v', ' mp2', ' mpv2', ' mp2v', ' mpa', ' mp3', ' m3u', ' mid', ' midi',
               ' rm', ' rma', ' rmi', ' rmv', ' aif', ' aifc', ' aiff', ' au', ' snd', ' flv', ' mp4', ' svg']



# Global OC utility variables
default_file_path = '/files/assets/'
default_shared_file_path = '/files/sharedassets/'


# Function to get, post, or delete files using the OC API.
def get_root_folders(admin_url, api_key, app_id, shared='false'):
    enc_shared = parse.quote(shared, safe='')
    url = admin_url + folders_endpoint + files_folder_get + '?FolderId=Folder_GroupFiles&isShared=' + enc_shared
    auth = authorize(url, api_key, app_id)
    request_headers = default_headers
    request_headers['Authorization'] = auth

    r = requests.get(url=url,
                     headers=request_headers)

    return r


def get_folder(folder_id, admin_url, api_key, app_id):

    return


def get_or_create_folder(path, admin_url, api_key, app_id, shared='false'):
    enc_path = parse.quote(path, safe='')
    enc_shared = parse.quote(shared, safe='')
    url = admin_url + folders_endpoint + folder_getOrCreateByPath + '?path=' + enc_path + '&isShared=' + enc_shared
    auth = authorize(url, api_key, app_id)
    request_headers = default_headers
    request_headers['Authorization'] = auth

    r = requests.get(url=url,
                     headers=request_headers
                     )

    return r


def get_folder_files(folder_id, admin_url, api_key, app_id, file_name=None, shared=None):
    api_method = 'GET'
    url = admin_url + '/api/v1/folder/GetFiles?FolderId=' + folder_id
    if shared:
         url = url + '&isShared=' + shared

    if file_name:
        url = url + '&Name=' + file_name

    # Send request to OC API.
    auth = authorize(url, api_key, app_id)
    request_headers = default_headers
    request_headers['Authorization'] = auth

    response = requests.request(api_method,
                                url,
                                headers=request_headers)

    return response


def create_file(file, folder_id, admin_url, api_key, app_id, owner='admin'):
    api_method = 'POST'
    url = admin_url + '/api/v1/files/Create'
    file_name = file.split('/')[-1]
    extension = file_name.split('.')[-1]
    object_type = 'Document'
    auth = authorize(url, api_key, app_id, method=api_method)

    # Determine file and application type.
    if extension in media_types:
        object_type = 'Media'

    if extension in image_types:
        object_type = 'Image'

    # Build json body to send to API.
    payload = {
        'json': json.dumps(
            {
                "FolderId": folder_id,
                "FileObjectType": object_type,
                "Owner": owner,
                "Name": file_name,
                "IsShared": False
            }
        )
    }

    files = [
        (
            'file', (
                file_name,
                open(file, 'rb'),
                ''
            )
        )
    ]

    request_headers = default_headers
    request_headers['Authorization'] = auth

    response = requests.request(
        api_method,
        url,
        headers=request_headers,
        data=payload,
        files=files
    )

    return response


def get_file(file_id, admin_url, api_key, app_id):
    api_method = 'GET'
    url = admin_url + '/api/v1/files/get?FileId=' + file_id
    auth = authorize(url, api_key, app_id, method=api_method)
    request_headers = default_headers
    request_headers['Authorization'] = auth

    payload = requests.request(api_method,
                               url,
                               headers=request_headers)

    try:
        payload.raise_for_status()
    except requests.exceptions.HTTPError as err:
        print(err)

    return payload


def get_file_stream(file_id, admin_url, api_key, app_id):
    api_method = 'GET'
    url = admin_url + '/api/v1/files/getfilestream?FileId=' + file_id
    auth = authorize(url, api_key, app_id, method=api_method)
    request_headers = default_headers
    request_headers['Authorization'] = auth

    payload = requests.request(api_method,
                               url,
                               headers=request_headers)

    try:
        payload.raise_for_status()
    except requests.exceptions.HTTPError as err:
        print(err)

    return payload


def save_file(file_id, admin_url, api_key, app_id, save_path):
    api_method = 'GET'
    url = admin_url + '/api/v1/files/GetFileStream?FileId=' + file_id
    auth = authorize(url, api_key, app_id, method=api_method)
    request_headers = default_headers
    request_headers['Authorization'] = auth

    file_data = get_file(file_id, admin_url, api_key, app_id)
    metadata = file_data.json()
    if save_path[-1] == '/':
        save_path = save_path[0:-1]
    file_name = save_path + '/' + metadata['Name']

    with requests.request(api_method,url,headers=request_headers,stream=True) as payload:
        try:
            payload.raise_for_status()
        except requests.exceptions.HTTPError as err:
            print(err)
        with open(file_name, 'wb') as file:
            for chunk in payload.iter_content(chunk_size=8192):
                file.write(chunk)

    return file_name


def update_from_file(file, file_name, filepath, file_type, admin_url, api_key, app_id, owner=None):
    api_method = 'POST'
    url = admin_url + files_endpoint + files_folder_update
    auth = authorize(url, api_key, app_id, method=api_method)
    request_headers = default_headers
    request_headers['Authorization'] = auth
    if owner:
        file['Owner'] = owner

    payload = {
        'json': json.dumps(
            {
                "FileId": file['FileId'],
                "FolderId": file['FolderId'],
                "FileObjectType": file_type,
                "Owner": file['Owner'],
                "Name": file_name
            }
        )
    }

    files = [
        (
            'file', (
                file_name,
                open(filepath, 'rb'),
                ''
            )
        )
    ]

    response = requests.request(
        api_method,
        url,
        headers=request_headers,
        data=payload,
        files=files
    )

    return response


def updated_file(file, folder_id, admin_url, api_key, app_id, owner='admin'):
    api_method = 'POST'
    url = admin_url + '/api/v1/files/Create'
    file_name = file.split('/')[-1]
    extension = file_name.split('.')[-1]
    object_type = 'Document'
    auth = authorize(url, api_key, app_id, method=api_method)

    # Determine file and application type.
    if extension in media_types:
        object_type = 'Media'

    if extension in image_types:
        object_type = 'Image'

    # Build json body to send to API.
    payload = {
        'json': json.dumps(
            {
                "FolderId": folder_id,
                "FileObjectType": object_type,
                "Owner": owner,
                "Name": file_name
            }
        )
    }

    files = [
        (
            'file', (
                file_name,
                open(file, 'rb'),
                ''
            )
        )
    ]

    request_headers = default_headers
    request_headers['Authorization'] = auth

    response = requests.request(
        api_method,
        url,
        headers=request_headers,
        data=payload,
        files=files
    )

    return response


def create_or_update_file(file, folder_id, admin_url, api_key, app_id):
    file_name = file.split('/')[-1]
    # Check if file already exists.
    exists = False
    file_check = get_folder_files(folder_id, admin_url, api_key, app_id, file_name=file_name)
    file_check = file_check.json()
    exist_files = [x['Name'] for x in file_check]

    if file_name in exist_files:
        exists = True

    # Create the file using the OC API.
    if exists:
        response = updated_file(file,
                                folder_id,
                                admin_url,
                                api_key,
                                app_id)
    else:
        response = create_file(file,
                               folder_id,
                               admin_url,
                               api_key,
                               app_id)

    return response


def create_file_from_link(link, admin_url, api_key, app_id, folder_id=None, owner='admin'):
    file_data = requests.request('GET', link)
    api_method = 'POST'
    url = admin_url + files_endpoint + files_folder_create
    file_name = link.split('/')[-1]
    extension = file_name.split('.')[-1]
    object_type = 'Document'
    auth = authorize(url, api_key, app_id, method=api_method)

    # Determine file and application type.
    if extension in media_types:
        object_type = 'Media'

    if extension in image_types:
        object_type = 'Image'

    # Create or get folder if no ID provided
    if not folder_id:
        folder_path = ''
        if len(link.split(default_file_path)) > 1:
            path_parts = link.split(default_file_path)[1].split('/')[1:-1]
            folder_shared = 'false'
        else:
            path_parts = link.split(default_shared_file_path)[1].split('/')[1:-1]
            folder_shared = 'true'
        for part in path_parts:
            folder_path = folder_path + '/' + part
        folder_data = get_or_create_folder(folder_path, admin_url, api_key, app_id, shared=folder_shared)
        folder_data = folder_data.json()
        folder_id = folder_data['FolderId']

    # Build json body to send to API.
    payload = {
        'json': json.dumps(
            {
                "FolderId": folder_id,
                "FileObjectType": object_type,
                "Owner": owner,
                "Name": file_name
            }
        )
    }

    files = [
        (
            'file', (
                file_name,
                file_data.content,
                ''
            )
        )
    ]

    request_headers = default_headers
    request_headers['Authorization'] = auth

    response = requests.request(
        api_method,
        url,
        headers=request_headers,
        data=payload,
        files=files
    )

    return response


def update_file_from_link(link, admin_url, api_key, app_id, folder_id=None, owner='admin'):
    file_data = requests.request('GET', link)
    api_method = 'POST'
    url = admin_url + files_endpoint + files_folder_update
    file_name = link.split('/')[-1]
    extension = file_name.split('.')[-1]
    object_type = 'Document'
    auth = authorize(url, api_key, app_id, method=api_method)

    # Determine file and application type.
    if extension in media_types:
        object_type = 'Media'

    if extension in image_types:
        object_type = 'Image'

    # Create or get folder if no ID provided
    if len(link.split(default_file_path)) > 1:
        path_parts = link.split(default_file_path)[1].split('/')[1:-1]
        folder_shared = 'false'
    else:
        path_parts = link.split(default_shared_file_path)[1].split('/')[1:-1]
        folder_shared = 'true'
    if not folder_id:
        folder_path = ''
        for part in path_parts:
            folder_path = folder_path + '/' + part
        folder_data = get_or_create_folder(folder_path, admin_url, api_key, app_id, shared=folder_shared)
        folder_data = folder_data.json()
        folder_id = folder_data['FolderId']

    # Get file ID from folder
    folder_files = get_folder_files(folder_id, admin_url, api_key, app_id, file_name=file_name, shared=folder_shared)
    folder_files_data = folder_files.json()
    file_id = folder_files_data[0]['FileId']

    # Build json body to send to API.
    payload = {
        'json': json.dumps(
            {
                "FileId": file_id,
                "FolderId": folder_id,
                "FileObjectType": object_type,
                "Owner": owner,
                "Name": file_name
            }
        )
    }

    files = [
        (
            'file', (
                file_name,
                file_data.content,
                ''
            )
        )
    ]

    request_headers = default_headers
    request_headers['Authorization'] = auth

    response = requests.request(
        api_method,
        url,
        headers=request_headers,
        data=payload,
        files=files
    )

    return response


def create_or_update_file_from_link(link, admin_url, api_key, app_id, folder_id=None, owner='admin'):
    file_exists = False
    file_data = requests.request('GET', link)
    api_method = 'POST'
    file_name = link.split('/')[-1]
    extension = file_name.split('.')[-1]
    object_type = 'Document'

    # Determine file and application type.
    if extension in media_types:
        object_type = 'Media'

    if extension in image_types:
        object_type = 'Image'

    # Create or get folder if no ID provided
    if len(link.split(default_file_path)) > 1:
        path_parts = link.split(default_file_path)[1].split('/')[1:-1]
        folder_shared = 'false'
    else:
        path_parts = link.split(default_shared_file_path)[1].split('/')[1:-1]
        folder_shared = 'true'
    if not folder_id:
        folder_path = ''
        for part in path_parts:
            folder_path = folder_path + '/' + part
        folder_data = get_or_create_folder(folder_path, admin_url, api_key, app_id, shared=folder_shared)
        folder_data = folder_data.json()
        folder_id = folder_data['FolderId']

    # Get file ID from folder
    folder_files = get_folder_files(folder_id, admin_url, api_key, app_id, file_name=file_name, shared=folder_shared)
    folder_files_data = folder_files.json()

    if len(folder_files_data) > 0:
        file_exists = True
        file_id = folder_files_data[0]['FileId']

    # Build json body to send to API.
    files = [
        (
            'file', (
                file_name,
                file_data.content,
                ''
            )
        )
    ]

    if file_exists:
        payload = {
            'json': json.dumps(
                {
                    "FileId": file_id,
                    "FolderId": folder_id,
                    "FileObjectType": object_type,
                    "Owner": owner,
                    "Name": file_name
                }
            )
        }
        url = admin_url + files_endpoint + files_folder_update
    else:
        payload = {
            'json': json.dumps(
                {
                    "FolderId": folder_id,
                    "FileObjectType": object_type,
                    "Owner": owner,
                    "Name": file_name
                }
            )
        }
        url = admin_url + files_endpoint + files_folder_create

    auth = authorize(url, api_key, app_id, method=api_method)
    request_headers = default_headers
    request_headers['Authorization'] = auth

    response = requests.request(
        api_method,
        url,
        headers=request_headers,
        data=payload,
        files=files
    )

    return response


def get_folders(admin_url, api_key, app_id, shared=False):
    root_path = 'Folder_GroupFiles'
    if shared:
        root_path = 'Folder_SharedFiles'
    url = admin_url + folders_endpoint + '/get?FolderId=' + root_path + '&isShared=' + str(shared).lower()
    auth = authorize(url, api_key, app_id)
    request_header = default_headers
    request_header['Authorization'] = auth

    r = requests.get(url=url,
                     headers=request_header)

    folder_list = r.json()

    return folder_list


def add_root_paths(folder_list):
    for folder in folder_list:
        folder['Path'] = '/' + folder['Name']

    return folder_list


def get_descendant_folders(full_list, start_list, admin_url, api_key, app_id):
    for folder in full_list:
        if folder['FolderId'] != 'Folder_GroupFiles' and folder['FolderId'] != 'Folder_SharedFiles':
            url = admin_url + '/api/v1/folder/GetChildFolders?FolderId=' + folder['FolderId']
            auth = authorize(url, api_key, app_id)
            request_header = default_headers
            request_header['Authorization'] = auth
            r = requests.get(url=url,
                             headers=request_header)
            child_folders = r.json()

            if len(child_folders) > 0:
                for child in child_folders:
                    child['Path'] = folder['Path'] + '/' + child['Name']
                    start_list.append(child)
                get_descendant_folders(child_folders, start_list, admin_url, api_key, app_id)

    return start_list
