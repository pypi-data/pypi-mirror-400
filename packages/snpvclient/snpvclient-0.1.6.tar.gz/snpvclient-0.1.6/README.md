# Supernote Private Cloud Python Client

A Python client for connecting to a Supernote Private Cloud Instance. Useful for automating tasks like uploading content to your Supernote device.

Requires Python 3.10+

## Install

```
pip install snpvclient
```

## Usage and Examples

Setup the client and connect to private cloud.
```python
import snpvclient as sn
snclient = sn.SNPClient( 'https://supernote.example.com' )
snclient.login( 'email@example.com', 'password' )
```

Get root folder and file list
```python
root_folder = snclient.getList()
```

Get list of folders and files for a specific ```id```
```python
folder_list = snclient.getList( '78236046000054508' ) # id
```

Upload a file
```python
upload = snclient.upload(file_path, directoryId)
```

Delete a file
```python
delete = snclient.delete( 'directoryId', [ 'document id', 'document id' ] )
```

Get url of rendered PNG of all pages of a .note file.
```python
png = snclient.getPNG( 'document id' )
```

Get url of all rendered PDF of a .note file. Pass specific page numbers as a list or a blank list for all pages.
```python
pdf = snclient.getPDF( 'document id', [ 'pageNo' ] )
```

## Actions

List all folders and files

```python
sn.actions.list_folder( snclient )
```

Upload to a specific folder on your device. In this case, it will upload ```test_file.pdf``` to ```Research``` folder under the main ```Note``` folder.

```python
sn.actions.upload_to_folder( snclient, 'test_file.pdf', 'Note/Research')
```

You can also use the shortcut action to common Supernote folders

```python
sn.actions.upload_to_inbox( snclient, 'test_file.pdf' ) # Inbox
sn.actions.upload_to_document( snclient, 'test_file.pdf' ) # Document
sn.actions.upload_to_note( snclient, 'test_file.pdf' ) # Note
```