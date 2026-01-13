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
from typing import List
from datetime import date

@dataclass
class ForeignPriority:
    """Represents a foreign priority claim"""
    office_name: str
    filing_date: date
    application_number: str

    @classmethod
    def from_dict(cls, data: dict) -> 'ForeignPriority':
        return cls(
            office_name=data.get('ipOfficeName', ''),
            filing_date=date.fromisoformat(data.get('filingDate', '1900-01-01')),
            application_number=data.get('applicationNumberText', '')
        )

@dataclass
class ForeignPriorityData:
    """Represents foreign priority data for a patent application"""
    application_number: str
    foreign_priorities: List[ForeignPriority] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict) -> 'ForeignPriorityData':
        return cls(
            application_number=data.get('applicationNumberText', ''),
            foreign_priorities=[
                ForeignPriority.from_dict(fp) 
                for fp in data.get('foreignPriorityBag', [])
            ]
        )

@dataclass
class ForeignPriorityCollection:
    """Collection of foreign priority data"""
    count: int
    priorities: List[ForeignPriorityData] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict) -> 'ForeignPriorityCollection':
        return cls(
            count=data.get('count', 0),
            priorities=[
                ForeignPriorityData.from_dict(pw) 
                for pw in data.get('patentFileWrapperDataBag', [])
            ]
        )
