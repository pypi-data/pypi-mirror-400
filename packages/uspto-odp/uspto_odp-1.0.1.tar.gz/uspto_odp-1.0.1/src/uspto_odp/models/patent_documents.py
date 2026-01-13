'''
MIT License

Copyright (c) 2024 Ken Thompson, https://github.com/KennethThompson, all rights reserved.

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
'''
from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime
import re

@dataclass
class DownloadOption:
    """Represents a document download option"""
    mime_type: str
    download_url: str
    page_count: Optional[int] = None

    @classmethod
    def from_dict(cls, data: dict) -> 'DownloadOption':
        return cls(
            mime_type=data['mimeTypeIdentifier'],
            download_url=data['downloadUrl'],
            page_count=data.get('pageTotalQuantity')
        )

@dataclass
class PatentDocument:
    """Represents a single patent document"""
    application_number: str
    official_date: datetime
    document_identifier: str
    document_code: str
    document_description: str
    direction_category: str
    download_options: List[DownloadOption] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict) -> 'PatentDocument':
        # Format the timezone offset to include a colon
        date_str = data['officialDate']
        
        # Remove any existing timezone formatting first
        if date_str.endswith('Z'):
            date_str = date_str[:-1] + '+00:00'
        else:
            # Handle timezone offset without colon (e.g., -0500 -> -05:00)
            if match := re.search(r'([+-])(\d{2})(\d{2})$', date_str):
                sign, hours, minutes = match.groups()
                date_str = date_str[:-5] + f"{sign}{hours}:{minutes}"
        
        return cls(
            application_number=data['applicationNumberText'],
            official_date=datetime.fromisoformat(date_str),
            document_identifier=data['documentIdentifier'],
            document_code=data['documentCode'],
            document_description=data['documentCodeDescriptionText'],
            direction_category=data['directionCategory'],
            download_options=[DownloadOption.from_dict(opt) for opt in data.get('downloadOptionBag', [])]
        )

@dataclass
class PatentDocumentCollection:
    """Collection of patent documents"""
    documents: List[PatentDocument] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict) -> 'PatentDocumentCollection':
        return cls(
            documents=[PatentDocument.from_dict(doc) for doc in data.get('documentBag', [])]
        )
