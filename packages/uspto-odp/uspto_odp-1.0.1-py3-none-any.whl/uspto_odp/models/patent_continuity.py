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

from uspto_odp.models.patent_status import ApplicationStatus


@dataclass
class ParentContinuity:
    """Represents a parent continuity relationship"""
    parent_status_code: int
    parent_status_description: str
    parent_filing_date: date
    parent_application_number: str
    child_application_number: str
    claim_parentage_code: str
    claim_parentage_description: str
    first_inventor_to_file: bool = False
    parent_patent_number: Optional[str] = None

    @classmethod
    def from_dict(cls, data: dict) -> 'ParentContinuity':
        return cls(
            first_inventor_to_file=data.get('firstInventorToFileIndicator', False),
            parent_status_code=data.get('parentApplicationStatusCode', 0),
            parent_status_description=data.get('parentApplicationStatusDescriptionText', ''),
            parent_filing_date=date.fromisoformat(data.get('parentApplicationFilingDate', '1900-01-01')),
            parent_application_number=data.get('parentApplicationNumberText', ''),
            child_application_number=data.get('childApplicationNumberText', ''),
            claim_parentage_code=data.get('claimParentageTypeCode', ''),
            claim_parentage_description=data.get('claimParentageTypeCodeDescription', ''),
            parent_patent_number=data.get('parentPatentNumber')
        )
    @property
    def status(self) -> str:
        """Returns the string description of the application status"""
        try:
            return ApplicationStatus(str(self.parent_status_code)).name.replace('_', ' ').title()
        except ValueError:
            return f"Unknown Status Code: {self.parent_status_code}"

@dataclass
class ChildContinuity:
    """Represents a child continuity relationship"""
    child_status_code: int
    parent_application_number: str
    child_application_number: str
    child_status_description: str
    child_filing_date: date
    claim_parentage_code: str
    claim_parentage_description: str
    first_inventor_to_file: bool = False
    child_patent_number: Optional[str] = None

    @classmethod
    def from_dict(cls, data: dict) -> 'ChildContinuity':
        return cls(
            child_status_code=data.get('childApplicationStatusCode', 0),
            parent_application_number=data.get('parentApplicationNumberText', ''),
            child_application_number=data.get('childApplicationNumberText', ''),
            child_status_description=data.get('childApplicationStatusDescriptionText', ''),
            child_filing_date=date.fromisoformat(data.get('childApplicationFilingDate', '1900-01-01')),
            first_inventor_to_file=data.get('firstInventorToFileIndicator', False),
            claim_parentage_code=data.get('claimParentageTypeCode', ''),
            claim_parentage_description=data.get('claimParentageTypeCodeDescription', ''),
            child_patent_number=data.get('childPatentNumber')
        )
    @property
    def status(self) -> str:
        """Returns the string description of the application status"""
        try:
            return ApplicationStatus(str(self.child_status_code)).name.replace('_', ' ').title()
        except ValueError:
            return f"Unknown Status Code: {self.child_status_code}"
@dataclass
class ContinuityData:
    """Represents continuity data for a patent application"""
    application_number: str
    parent_continuities: List[ParentContinuity] = field(default_factory=list)
    child_continuities: List[ChildContinuity] = field(default_factory=list)
    request_identifier: Optional[str] = None

    @classmethod
    def from_dict(cls, data: dict) -> 'ContinuityData':
        return cls(
            application_number=data['applicationNumberText'],
            parent_continuities=[ParentContinuity.from_dict(p) for p in data.get('parentContinuityBag', [])],
            child_continuities=[ChildContinuity.from_dict(c) for c in data.get('childContinuityBag', [])],
            request_identifier=data.get('requestIdentifier')
        )

@dataclass
class ContinuityCollection:
    """Collection of continuity data"""
    count: int
    continuities: List[ContinuityData] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict) -> 'ContinuityCollection':
        return cls(
            count=data['count'],
            continuities=[ContinuityData.from_dict(pw) for pw in data.get('patentFileWrapperDataBag', [])]
        ) 
        
        
def get_earliest_parent_filing_date(parent_continuities: List[ParentContinuity]) -> Optional[date]:
    """
    Finds the earliest filing date among parent applications, ignoring provisional applications.
    
    Args:
        parent_continuities: List of ParentContinuity objects
        
    Returns:
        The earliest filing date found, or None if no valid dates exist
    """
    earliest_date = None
    
    for parent in parent_continuities:
        # Skip provisional applications
        if parent.claim_parentage_code == 'PRO':
            continue
            
        # Initialize earliest_date if not set
        if earliest_date is None:
            earliest_date = parent.parent_filing_date
            continue
            
        # Compare dates and keep the earlier one
        if parent.parent_filing_date < earliest_date:
            earliest_date = parent.parent_filing_date
            
    return earliest_date

