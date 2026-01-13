from typing import Any, Dict, Optional, Tuple

def get(self, endpoint: str, **kwargs) -> Any:
    return self._request('GET', endpoint, **kwargs)

def put(self, endpoint: str, **kwargs) -> Any:
    return self._request('PUT', endpoint, **kwargs)

def getPDFwithMark(self, id: str) -> Any:
    """
    Get PDF file with marks from Supernote Private Cloud Instance.
    """
    
    payload = {
        "id": id
    }

    headers = {
        "x-access-token": self._token,
    }

    return self.post('pdfwithmark', json=payload, headers=headers)