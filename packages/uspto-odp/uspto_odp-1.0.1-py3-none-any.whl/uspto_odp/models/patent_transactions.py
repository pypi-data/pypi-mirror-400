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
from datetime import date

@dataclass
class TransactionEvent:
    """Represents a single transaction event"""
    event_code: str
    event_description: str
    event_date: date

    @classmethod
    def from_dict(cls, data: dict) -> 'TransactionEvent':
        return cls(
            event_code=data.get('eventCode', ''),
            event_description=data.get('eventDescriptionText', ''),
            event_date=date.fromisoformat(data.get('eventDate', '1900-01-01'))
        )

@dataclass
class ApplicationTransactions:
    """Represents all transactions for a patent application"""
    application_number: str
    events: List[TransactionEvent] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict) -> 'ApplicationTransactions':
        return cls(
            application_number=data.get('applicationNumberText', ''),
            events=[TransactionEvent.from_dict(event) 
                   for event in data.get('eventDataBag', [])]
        )

@dataclass
class TransactionCollection:
    """Collection of transaction data"""
    count: int
    transactions: List[ApplicationTransactions] = field(default_factory=list)
    request_identifier: Optional[str] = None

    @classmethod
    def from_dict(cls, data: dict) -> 'TransactionCollection':
        return cls(
            count=data.get('count', 0),
            transactions=[ApplicationTransactions.from_dict(pw) 
                         for pw in data.get('patentFileWrapperDataBag', [])],
            request_identifier=data.get('requestIdentifier')
        )
