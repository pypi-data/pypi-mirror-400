import os
from typing import TYPE_CHECKING, Any, Dict, Optional, Tuple

# This is for coding hints only to avoid circular imports
if TYPE_CHECKING:
    from .client import SNPClient
    from .exceptions import *

def list_folder( client, folder_id: str = None, indent=0 ):
    """
    List files and folders in the specified folder.
    """
    l = client.getList( folder_id )
    if ( 'success', True ) in l.items():
        for item in l.get( 'userFileVOList', [] ):
            name = item.get( 'fileName', '' )
            is_folder = item.get( 'isFolder' ) == 'Y'
            prefix = '  ' * indent
            if is_folder:
                print( f"{prefix}[D] {name} ({item.get('id')})" )
                list_folder( client, item.get('id'), indent + 1 )
            else:
                size = item.get( 'size', 0 )
                try:
                    size_bytes = int( size )
                except ( TypeError, ValueError ):
                    try:
                        size_bytes = int( float( size ) )
                    except Exception:
                        size_bytes = 0
                size_mb = size_bytes / ( 1024 * 1024 )
                print(f"{prefix}- {name} ({item.get('id')}) {size_mb:.2f} MB")
    else:
        print( 'Failed to list folder', folder_id )

def upload_to_folder( client, file_path: str, folder: str ) -> Any:
    """
    Upload a file to the specified folder.
    """

    dir = client.find_folder( folder )

    if not dir:
        raise FolderNotFoundError( f"Folder '{folder}' not found." )

    return client.upload( file_path, dir )


def upload_to_inbox( client, file_path: str ) -> Any:
    """
    Upload a file to INBOX folder.
    """

    return upload_to_folder( client, file_path, 'Inbox' )

def upload_to_document( client, file_path: str ) -> Any:
    """
    Upload a file to Documents folder.
    """

    return upload_to_folder( client, file_path, 'Document' )

def upload_to_note( client, file_path: str ) -> Any:
    """
    Upload a file to Note folder.
    """

    return upload_to_folder( client, file_path, 'Note' )