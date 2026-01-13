import os
from pathlib import Path
from typing import Any, Dict, Optional, Tuple
from urllib.parse import urlparse, parse_qs
import requests as rq

from .api import endpoints
from .utils import getSHA256, getMD5
from .actions import *
from .exceptions import *


class SNPClient:
    """
    API client for connecting to Supernote Private Cloud Instance.
    """

    def __init__( self, host: Optional[ str ] = None, timeout: int = 30 ):
        self.host = host
        self.timeout = timeout
        self.session = rq.Session()

    def _build_url( self, endpoint: str ) -> str:
        """
        Return a full URL for a named endpoint.
        """
        return f"{ self.host }{ endpoints[ endpoint ] }"

    def _request( self, method: str, endpoint: str, **kwargs ) -> Any:
        """
        Generic request wrapper that raises for HTTP errors and
        returns JSON when possible, otherwise raw text.
        """
        
        url = self._build_url( endpoint )
        resp = self.session.request( method, url, timeout=self.timeout, **kwargs )
        resp.raise_for_status()

        try:
            return resp.json()
        except ValueError:
            return resp.text

    def post( self, endpoint: str, **kwargs ) -> Any:
        """
        Send a POST request to the specified endpoint.
        """
        return self._request( 'POST', endpoint, **kwargs )
    
    def _get_code( self, email: str ) -> Tuple[ str, str ]:
        """
        Get verification code from Supernote Private Cloud Instance.
        """
        payload = {
            "countryCode": 1,
            "account": email
        }

        response = self.post( 'code', json=payload )
        return ( response[ 'randomCode' ], response[ 'timestamp' ] )
        
    def login(self, email: str, password: str) -> str:
        """
        Login to Supernote Private Cloud Instance with email and password.
        """

        ( code, timestamp ) = self._get_code( email )

        passcode = getSHA256( getMD5( password ) + code )

        payload = {
            "countryCode": 1,
            "account": email,
            "password": passcode,
            "browser": "Chrome143",
            "equipment": "1",
            "loginMethod": "1",
            "timestamp": timestamp,
            "language": "en",
        }

        login_response = self.post( 'login', json=payload )

        self._token = login_response[ 'token' ]

        return login_response[ 'token' ]
    
    def getList( self, directoryId: str = None, page: int = 1, pageSize: int = 20 ) -> Dict[ str, Any ]:
        """
        Get list of files and directories in the specified directory.
        Uses root as the default directory.
        """

        payload = {
            "directoryId": directoryId or 0, # 0 is the root directory
            "pageNo": page,
            "pageSize": pageSize,
            "sequence":"desc",
            "order":"time"
            }
        
        headers = {
            "x-access-token": self._token,
        }

        return self.post( 'list', json=payload, headers=headers )
    
    def find_root_folder( self, folder_name: str ) -> str:
        """
        Find folder ID by folder name in the root directory.
        """

        root_folder = self.getList( )

        for item in root_folder.get( 'userFileVOList', [] ):
            if item.get( 'isFolder' ) == 'Y' and item.get( 'fileName' ) == folder_name:
                return item.get( 'id' )
        
        return ''
    
    def find_folder( self, folder_path: str ) -> str:
        """
        Find folder ID by folder path.
        """
        parts = Path( folder_path ).parts

        # Remove leading slash part
        if parts[0] == '/':
            parts = parts[1:]

        # Start from root
        folder = self.getList(  )

        for part in parts:
            found = False
            for item in folder.get( 'userFileVOList', [] ):
                if item.get( 'isFolder' ) == 'Y' and item.get( 'fileName' ) == part:
                    folder = self.getList( item.get( 'id' ) )
                    found = True
                    break
            if not found:
                return ''
            
        return item.get( 'id' )
    
    def getPNG( self, id: str ) -> Any:
        """
        Get PNG image from .note file.
        """

        payload = {
            "id": id
        }

        headers = {
            "x-access-token": self._token,
        }

        png_response = self.post( 'png', json=payload, headers=headers )

        return png_response.get( 'pngPageVOList', [] )
    
    def download( self, id: str, type: int = 0 ) -> Any:
        """
        Get download URL for a file from Supernote Private Cloud Instance.
        Downloads the unpprocessed file.
        """

        payload = {
            "id": id,
            "type": type
        }

        headers = {
            "x-access-token": self._token,
        }

        download_response = self.post( 'download', json=payload, headers=headers )

        return download_response.get( 'url', '' )

    def getPDF( self, id: str, pageList: list = [] ) -> Any:
        """
        Get PDF file from .note file.
        """

        payload = {
            "id": id,
            "pageNoList": pageList
        }

        headers = {
            "x-access-token": self._token,
        }

        pdf_response = self.post( 'pdf', json=payload, headers=headers )

        return pdf_response.get( 'url', '' )

    def upload( self, file_path: str, dir: str ) -> Any:
        """
        Upload a file to Supernote Private Cloud Instance.
        """

        # Check if file exists
        if not os.path.exists( file_path ):
            return 0

        with open( file_path, 'rb' ) as file:
            file_data = file.read()
            file_md5 = getMD5( file_data )

        file_name = os.path.basename( file_path )

        payload = {
            "directoryId": dir,
            "fileName": file_name,
            "md5": file_md5,
            "size": len( file_data )
        }

        headers = {
            "x-access-token": self._token,
        }

        # Apply to upload file to server
        apply_response = self.post( 'apply', json=payload, headers=headers )

        if ( 'success', True ) not in apply_response.items():
            return { 'success': 0, 'message': apply_response.get( 'errorMsg', 'Apply upload failed' ) }

        inner_name = apply_response[ 'innerName' ]

        upload_url = apply_response[ 'fullUploadUrl' ]

        parsed_url = urlparse( upload_url )
        query_params = parse_qs( parsed_url.query )

        file_form = {
            'name': 'file',
            'filename': inner_name,
        }

        # Actually upload file
        with open( file_path, 'rb' ) as f:
            upload_response = self.post( 'upload', params=query_params, files={ 'file': f }, data=file_form, headers=headers )

        if ( 'success', True ) not in upload_response.items():
            return { 'success': 0, 'message': upload_response.get( 'errorMsg', 'Upload failed' ) }

        # Finish the upload process
        payload = {
            "directoryId": dir,
            "fileName": file_name,
            "fileSize": len( file_data ),
            "innerName": inner_name,
            "md5": file_md5
        }

        finish_response = self.post( 'finish', json=payload, headers=headers )

        if ( 'success', True ) not in finish_response.items():
            return { 'success': 0, 'message': finish_response.get('errorMsg', 'Finish upload failed') }
        else:
            return { 'success': 1, 'message': 'Upload successful' }

    def delete( self, directory_id: str, ids: list ) -> Any:
        """
        Delete a list of files from Supernote Private Cloud Instance.
        """

        payload = {
            "directoryId": directory_id,
            "idList": ids
        }
        
        headers = {
            "x-access-token": self._token,
        }

        return self.post( 'delete', json=payload, headers=headers )