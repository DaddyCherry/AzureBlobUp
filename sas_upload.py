from datetime import datetime, timedelta
from azure.storage.blob import BlobClient, generate_blob_sas, BlobSasPermissions, ContentSettings
from azure.keyvault.secrets import SecretClient
from azure.identity import DefaultAzureCredential

import pyperclip
import os
import datetime
import glob
import mimetypes



def get_blob_sas(account_name, account_key, container_name, blob_name):
    sas_blob = generate_blob_sas(account_name=account_name,
                                 container_name=container_name,
                                 blob_name=blob_name,
                                 account_key=account_key,
                                 permission=BlobSasPermissions(read=True),
                                 # start=datetime.utcnow(),
                                 expiry=datetime.datetime.utcnow() + timedelta(hours=3000000))
    return sas_blob


def upload_blob(connect_str, filename):
    file = filename
    file_name = os.path.basename(file).replace(' ', '_')
    root, ext = os.path.splitext(file)

    content_type = mimetypes.guess_type(file_name)[0]

    blob = BlobClient.from_connection_string(conn_str=connect_str, container_name='delivery', blob_name=file_name)
    with open(file, 'rb') as data:
        blob.upload_blob(data, overwrite=True, content_settings=ContentSettings(content_type=content_type))
    print(blob.url)
    pyperclip.copy(blob.url)


def main():
    file_path = pyperclip.paste()
    filename = file_path.replace(' ', '_')
    # os.rename(latest_file, filename)
    print('filename=', filename)

    key_vault_url = 'https://delivery.vault.azure.net/'

    credential = DefaultAzureCredential()
    client = SecretClient(vault_url=key_vault_url, credential=credential)
    blob_connect_str = client.get_secret('blob-connect-str')
    print(blob_connect_str.value)

    upload_blob(blob_connect_str.value, filename)

    account_name = 'delivery1213'
    account_key = blob_connect_str.value.split(';')[2].replace('AccountKey=', '')
    print('account_key', account_key)
    container_name = 'delivery'
    blob_name = os.path.basename(filename)

    blob = get_blob_sas(account_name, account_key, container_name, blob_name)
    url = 'https://' + account_name + '.blob.core.windows.net/' + container_name + '/' + blob_name + '?' + blob

    print(url)
    pyperclip.copy(url)

    return


if __name__ == '__main__':
    main()
