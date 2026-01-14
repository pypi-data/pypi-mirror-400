# IMPORT PACKAGES
from .authorization import basic_auth
import requests
import json
from urllib import parse
import re

# Global API variables
api_endpoint = '/api/v1'
page_get = '/get'
page_list = '/list'
type_list = '/contenttypes/list'
page_create = '/create'
page_update = '/update'
page_archive = '/archive'
page_fileupload = '/fileupload'
page_delete = '/delete'
default_headers = {'accept': 'application/json',
                   'user-agent': 'govAccess/Implementation'}

# Global OC utility variables
default_file_path = '/files/assets/'
default_shared_file_path = '/files/sharedassets/'


# List content types
def list_contenttypes(admin_url, api_key, app_id):
    auth = basic_auth(api_key, app_id)
    if admin_url[-1] == '/':
        admin_url = admin_url[0:-1]
    url = admin_url + api_endpoint + type_list
    request_headers = default_headers
    request_headers['Authorization'] = auth

    payload = requests.request('GET',
                               url,
                               headers=request_headers)

    try:
        payload.raise_for_status()
    except requests.exceptions.HTTPError as err:
        print(err)

    return payload


# List content type endpoints based on list of content types
def contenttype_endpoints(content_types):
    endpoints = [x['EndPointName'] for x in content_types]

    return endpoints


# List pages for a specified content type
def list_pages(admin_url, api_key, app_id, content_type, queries: dict = None):
    auth = basic_auth(api_key, app_id)
    if admin_url[-1] == '/':
        admin_url = admin_url[0:-1]
    url = admin_url + api_endpoint + '/' + page_get + content_type + page_list
    request_headers = default_headers
    request_headers['Authorization'] = auth
    if queries:
        for key in queries:
            if '?' not in url:
                url = url + '?' + key + '=' + parse.quote(queries[key], safe='')
            else:
                url = url + '&' + key + '=' + parse.quote(queries[key], safe='')

    payload = requests.request('GET',
                               url,
                               headers=request_headers)

    try:
        payload.raise_for_status()
    except requests.exceptions.HTTPError as err:
        print(err)

    return payload


# Get a page by ID
def get_page(admin_url, api_key, app_id, content_type, page_id, language=None):
    auth = basic_auth(api_key, app_id)
    url = admin_url + api_endpoint + '/' + content_type + page_get + '?id=' + parse.quote(page_id, safe='')
    request_headers = default_headers
    request_headers['Authorization'] = auth

    if language:
        url = url + '&language=' + language

    payload = requests.request('GET',
                               url,
                               headers=request_headers)

    try:
        payload.raise_for_status()
    except requests.exceptions.HTTPError as err:
        print(err)

    return payload


# Get all pages for all content types
def get_all_pages(admin_url, api_key, app_id):
    all_pages = list()
    all_types = list_contenttypes(admin_url, api_key, app_id)
    endpoints = all_types.json()
    endpoints = [x['EndPointName'] for x in endpoints]

    for endpoint in endpoints:
        this_pages = list_pages(admin_url, api_key, app_id, endpoint)
        this_pages = this_pages.json()
        if isinstance(this_pages, dict):
            for page in this_pages['Items']:
                page['contentType'] = endpoint
                all_pages.append(page)
        else:
            print('API Auth Error: ', this_pages)

    return all_pages


# Filter list of pages by selected parameters
def filter_pages(pages, key, keyword, language='en-US'):
    results = list()
    for page in pages:
        if key in page.keys():
            if keyword.lower() in page[key].lower():
                results.append(page)
        elif key in page['Locale'][language].keys():
            if keyword.lower() in page['Locale'][language][key].lower():
                results.append(page)
        elif key in page['Locale'][language]['PageDataField'].keys():
            if keyword.lower() in page['Locale'][language][key]['Value'].lower():
                results.append(page)

    return results


# Sort pages based on their level in the site map
def level_sort(pages, language='en-US', reverse=False):
    for page in pages:
        level = len(page['Locale'][language]['Link'].split('/')) - 1
        page['Order'] = level
    results = sorted(pages, key=lambda x: x['Order'], reverse=reverse)

    return results


# Identify the parent for each page
def add_parent(pages, language='en-US'):
    for page in pages:
        path = page['Locale'][language]['Link'].split('/')[0:-1]
        parent = path[0]
        path.pop(path.index(parent))
        for part in path:
            parent = parent + '/' + part
        page['Parent'] = parent

    return pages


# Match content types between two sites
def match_types(content_types, admin_url, api_key, app_id):
    new_types = list_contenttypes(admin_url, api_key, app_id)
    new_types = contenttype_endpoints(new_types.json())
    types_match = [x for x in content_types if x in new_types]

    return types_match


# Identify missing content types between two sites
def missing_types(content_types, admin_url, api_key, app_id):
    new_types = list_contenttypes(admin_url, api_key, app_id)
    new_types = contenttype_endpoints(new_types.json())
    types_miss = [x for x in content_types if x not in new_types]

    return types_miss


# Check whether a list of pages exists
def check_pages_exist(pages, admin_url, api_key, app_id):
    missing_pages = list()
    content_types = [x['contentType'] for x in pages]
    matching_types = match_types(content_types, admin_url, api_key, app_id)
    for this_type in matching_types:
        check_pages = [x for x in pages if x['contentType'] == this_type]
        new_pages = list_pages(admin_url, api_key, app_id, this_type)
        new_pages = new_pages.json()['Items']
        new_links = list()
        for new_page in new_pages:
            new_path = ''
            locale = list(new_page['Locale'].keys())[0]
            path_pieces = new_page['Locale'][locale]['Link'].split('/')[1:]
            for path in path_pieces:
                new_path = new_path + '/' + path
            new_links.append(new_path)
        for page in check_pages:
            check_link = ''
            locale = list(page['Locale'].keys())[0]
            path_pieces = page['Locale'][locale]['Link'].split('/')[1:]
            for path in path_pieces:
                check_link = check_link + '/' + path
            if check_link not in new_links:
                missing_pages.append(check_link)

    return missing_pages


# Identify field structures
def field_models(pages, language='en-US'):
    fields = dict()
    for page in pages:
        page_fields = page['Locale'][language]['PageDataField']
        for key in page_fields:
            if page_fields[key]['Type'] not in fields.keys():
                fields[page_fields[key]['Type']] = page_fields[key]

    return fields


# Find file links in pages
def find_files(pages, site_domain, language='en-US'):
    files = list()
    for page in pages:
        page_fields = page['Locale'][language]['PageDataField']
        for field in page_fields:
            if isinstance(page_fields[field]['Value'], str):
                field_value = page_fields[field]['Value']
            elif isinstance(page_fields[field]['Value'], dict):
                field_value = page_fields[field]['Value']['Value']
            if default_file_path in field_value:
                links = re.findall(default_file_path + '[^"]*', field['Value'])
                for link in links:
                    link = site_domain + link.split('/')[0]
                    files.append(link)
            elif default_shared_file_path in field_value:
                links = re.findall(default_file_path + '[^"]*', field['Value'])
                for link in links:
                    link = site_domain + link.split('/')[0]
                    files.append(link)

    return files


# Deprecated single function to get, post, or delete pages using the OC API.
def oc_api(url, api_key, app_id, method='GET', body=''):
    # Basic authentication
    auth = basic_auth(api_key, app_id)
    request_headers = default_headers
    request_headers['Content-Type'] = 'Application/json'
    request_headers['Authorization'] = auth

    if method == 'GET':
        r = requests.get(url=url,
                         headers=request_headers
                         )
    elif method == 'POST':
        r = requests.post(url=url,
                          data=json.dumps(body),
                          headers=request_headers
                          )
    else:
        r = requests.delete(url=url,
                            data=body,
                            headers=request_headers
                            )
    return r
