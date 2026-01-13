from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from datetime import datetime

@dataclass
class GrandDocumentMetaData:
    productIdentifier: Optional[str] = None
    zipFileName: Optional[str] = None
    fileCreateDateTime: Optional[str] = None
    xmlFileName: Optional[str] = None
    fileLocationURI: Optional[str] = None

@dataclass
class EventData:
    eventCode: Optional[str] = None
    eventDescriptionText: Optional[str] = None
    eventDate: Optional[str] = None

@dataclass
class EntityStatusData:
    smallEntityStatusIndicator: bool = False
    businessEntityStatusCategory: Optional[str] = None

@dataclass
class CorrespondenceAddress:
    cityName: Optional[str] = None
    geographicRegionName: Optional[str] = None
    geographicRegionCode: Optional[str] = None
    countryCode: Optional[str] = None
    postalCode: Optional[str] = None
    nameLineOneText: Optional[str] = None
    countryName: Optional[str] = None
    postalAddressCategory: Optional[str] = None
    addressLineOneText: Optional[str] = None
    addressLineTwoText: Optional[str] = None

@dataclass
class Inventor:
    firstName: Optional[str] = None
    lastName: Optional[str] = None
    countryCode: Optional[str] = None
    inventorNameText: Optional[str] = None
    correspondenceAddressBag: List[CorrespondenceAddress] = field(default_factory=list)

@dataclass
class Applicant:
    applicantNameText: Optional[str] = None
    correspondenceAddressBag: List[CorrespondenceAddress] = field(default_factory=list)

@dataclass
class ApplicationMetaData:
    firstInventorToFileIndicator: Optional[str] = None
    applicationStatusCode: Optional[int] = None
    applicationTypeCode: Optional[str] = None
    entityStatusData: Optional[EntityStatusData] = None
    filingDate: Optional[str] = None
    uspcSymbolText: Optional[str] = None
    nationalStageIndicator: Optional[bool] = False
    firstInventorName: Optional[str] = None
    cpcClassificationBag: List[str] = field(default_factory=list)
    effectiveFilingDate: Optional[str] = None
    publicationDateBag: List[str] = field(default_factory=list)
    publicationSequenceNumberBag: List[str] = field(default_factory=list)
    earliestPublicationDate: Optional[str] = None
    applicationTypeLabelName: Optional[str] = None
    applicationStatusDate: Optional[str] = None
    class_field: Optional[str] = None  # Using class_field as class is a reserved keyword
    applicationTypeCategory: Optional[str] = None
    inventorBag: List[Inventor] = field(default_factory=list)
    applicationStatusDescriptionText: Optional[str] = None
    patentNumber: Optional[str] = None
    grantDate: Optional[str] = None
    applicantBag: List[Applicant] = field(default_factory=list)
    firstApplicantName: Optional[str] = None
    customerNumber: Optional[int] = None
    groupArtUnitNumber: Optional[str] = None
    earliestPublicationNumber: Optional[str] = None
    inventionTitle: Optional[str] = None
    applicationConfirmationNumber: Optional[int] = None
    examinerNameText: Optional[str] = None
    subclass: Optional[str] = None
    publicationCategoryBag: List[str] = field(default_factory=list)
    docketNumber: Optional[str] = None

    def __post_init__(self):
        # Handle the "class" field which is a reserved Python keyword
        if hasattr(self, 'class'):
            self.class_field = getattr(self, 'class')
            delattr(self, 'class')

@dataclass
class ParentContinuity:
    parentApplicationStatusCode: Optional[int] = None
    firstInventorToFileIndicator: Optional[bool] = None
    claimParentageTypeCode: Optional[str] = None
    claimParentageTypeCodeDescriptionText: Optional[str] = None
    parentApplicationStatusDescriptionText: Optional[str] = None
    parentApplicationNumberText: Optional[str] = None
    parentApplicationFilingDate: Optional[str] = None
    childApplicationNumberText: Optional[str] = None
    parentPatentNumber: Optional[str] = None

@dataclass
class ChildContinuity:
    firstInventorToFileIndicator: Optional[bool] = None
    childApplicationStatusDescriptionText: Optional[str] = None
    claimParentageTypeCode: Optional[str] = None
    childApplicationStatusCode: Optional[int] = None
    claimParentageTypeCodeDescriptionText: Optional[str] = None
    parentApplicationNumberText: Optional[str] = None
    childApplicationFilingDate: Optional[str] = None
    childApplicationNumberText: Optional[str] = None

@dataclass
class PatentTermAdjustmentHistoryData:
    eventDescriptionText: Optional[str] = None
    eventSequenceNumber: Optional[float] = None
    originatingEventSequenceNumber: Optional[float] = None
    ptaPTECode: Optional[str] = None
    eventDate: Optional[str] = None

@dataclass
class PatentTermAdjustmentData:
    applicantDayDelayQuantity: Optional[int] = None
    overlappingDayQuantity: Optional[int] = None
    filingDate: Optional[str] = None
    ipOfficeAdjustmentDelayQuantity: Optional[int] = None
    cDelayQuantity: Optional[int] = None
    adjustmentTotalQuantity: Optional[int] = None
    bDelayQuantity: Optional[int] = None
    grantDate: Optional[str] = None
    aDelayQuantity: Optional[int] = None
    ipOfficeDayDelayQuantity: Optional[int] = None
    patentTermAdjustmentHistoryDataBag: List[PatentTermAdjustmentHistoryData] = field(default_factory=list)

@dataclass
class Assignor:
    executionDate: Optional[str] = None
    assignorName: Optional[str] = None

@dataclass
class AssigneeAddress:
    cityName: Optional[str] = None
    geographicRegionCode: Optional[str] = None
    postalCode: Optional[str] = None
    addressLineOneText: Optional[str] = None

@dataclass
class Assignee:
    assigneeAddress: Optional[AssigneeAddress] = None
    assigneeNameText: Optional[str] = None

@dataclass
class Assignment:
    assignmentReceivedDate: Optional[str] = None
    assignorBag: List[Assignor] = field(default_factory=list)
    frameNumber: Optional[int] = None
    reelAndFrameNumber: Optional[str] = None
    assignmentDocumentLocationURI: Optional[str] = None
    assignmentRecordedDate: Optional[str] = None
    conveyanceText: Optional[str] = None
    assigneeBag: List[Assignee] = field(default_factory=list)
    assignmentMailedDate: Optional[str] = None
    reelNumber: Optional[int] = None
    correspondenceAddressBag: List[CorrespondenceAddress] = field(default_factory=list)

@dataclass
class PGPubDocumentMetaData:
    productIdentifier: Optional[str] = None
    zipFileName: Optional[str] = None
    fileCreateDateTime: Optional[str] = None
    xmlFileName: Optional[str] = None
    fileLocationURI: Optional[str] = None

@dataclass
class TelecommunicationAddress:
    telecommunicationNumber: Optional[str] = None
    telecomTypeCode: Optional[str] = None

@dataclass
class Attorney:
    activeIndicator: Optional[str] = None
    firstName: Optional[str] = None
    lastName: Optional[str] = None
    registrationNumber: Optional[str] = None
    attorneyAddressBag: List[CorrespondenceAddress] = field(default_factory=list)
    telecommunicationAddressBag: List[TelecommunicationAddress] = field(default_factory=list)
    registeredPractitionerCategory: Optional[str] = None

@dataclass
class CustomerNumberCorrespondenceData:
    powerOfAttorneyAddressBag: List[CorrespondenceAddress] = field(default_factory=list)
    patronIdentifier: Optional[int] = None

@dataclass
class RecordAttorney:
    powerOfAttorneyBag: List[Attorney] = field(default_factory=list)
    customerNumberCorrespondenceData: Optional[CustomerNumberCorrespondenceData] = None

@dataclass
class PatentFileWrapperData:
    applicationNumberText: Optional[str] = None
    grantDocumentMetaData: Optional[GrandDocumentMetaData] = None
    eventDataBag: List[EventData] = field(default_factory=list)
    applicationMetaData: Optional[ApplicationMetaData] = None
    parentContinuityBag: List[ParentContinuity] = field(default_factory=list)
    patentTermAdjustmentData: Optional[PatentTermAdjustmentData] = None
    assignmentBag: List[Assignment] = field(default_factory=list)
    pgpubDocumentMetaData: Optional[PGPubDocumentMetaData] = None
    childContinuityBag: List[ChildContinuity] = field(default_factory=list)
    lastIngestionDateTime: Optional[str] = None
    recordAttorney: Optional[RecordAttorney] = None
    correspondenceAddressBag: List[CorrespondenceAddress] = field(default_factory=list)

@dataclass
class SearchResponse:
    count: int = 0
    patentFileWrapperDataBag: List[PatentFileWrapperData] = field(default_factory=list)
    requestIdentifier: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SearchResponse':
        """
        Parse the search response data into a SearchResponse object.
        
        Args:
            data (Dict[str, Any]): The raw JSON response from the API
            
        Returns:
            SearchResponse: A structured representation of the search results
        """
        result = cls(
            count=data.get('count', 0),
            requestIdentifier=data.get('requestIdentifier')
        )
        
        # Parse patent file wrapper data
        if 'patentFileWrapperDataBag' in data:
            for wrapper_data in data['patentFileWrapperDataBag']:
                patent_wrapper = PatentFileWrapperData(
                    applicationNumberText=wrapper_data.get('applicationNumberText')
                )
                
                # Parse grant document metadata
                if 'grantDocumentMetaData' in wrapper_data:
                    patent_wrapper.grantDocumentMetaData = GrandDocumentMetaData(
                        **wrapper_data['grantDocumentMetaData']
                    )
                
                # Parse event data bag
                if 'eventDataBag' in wrapper_data:
                    patent_wrapper.eventDataBag = [
                        EventData(**event_data) 
                        for event_data in wrapper_data['eventDataBag']
                    ]
                
                # Parse application metadata
                if 'applicationMetaData' in wrapper_data:
                    app_meta = wrapper_data['applicationMetaData']
                    entity_status = None
                    if 'entityStatusData' in app_meta:
                        entity_status = EntityStatusData(**app_meta['entityStatusData'])
                    
                    # Handle inventorBag
                    inventor_bag = []
                    if 'inventorBag' in app_meta:
                        for inventor_data in app_meta['inventorBag']:
                            inventor = Inventor(
                                firstName=inventor_data.get('firstName'),
                                lastName=inventor_data.get('lastName'),
                                countryCode=inventor_data.get('countryCode'),
                                inventorNameText=inventor_data.get('inventorNameText')
                            )
                            
                            # Parse correspondence addresses
                            if 'correspondenceAddressBag' in inventor_data:
                                inventor.correspondenceAddressBag = [
                                    CorrespondenceAddress(**addr) 
                                    for addr in inventor_data['correspondenceAddressBag']
                                ]
                            
                            inventor_bag.append(inventor)
                    
                    # Handle applicantBag
                    applicant_bag = []
                    if 'applicantBag' in app_meta:
                        for applicant_data in app_meta['applicantBag']:
                            applicant = Applicant(
                                applicantNameText=applicant_data.get('applicantNameText')
                            )
                            
                            # Parse correspondence addresses
                            if 'correspondenceAddressBag' in applicant_data:
                                applicant.correspondenceAddressBag = [
                                    CorrespondenceAddress(**addr) 
                                    for addr in applicant_data['correspondenceAddressBag']
                                ]
                            
                            applicant_bag.append(applicant)
                    
                    # Create ApplicationMetaData object with special handling for 'class'
                    app_meta_copy = app_meta.copy()
                    if 'class' in app_meta_copy:
                        app_meta_copy['class_field'] = app_meta_copy.pop('class')
                    
                    # Remove nested objects that are handled separately
                    if 'entityStatusData' in app_meta_copy:
                        app_meta_copy.pop('entityStatusData')
                    if 'inventorBag' in app_meta_copy:
                        app_meta_copy.pop('inventorBag')
                    if 'applicantBag' in app_meta_copy:
                        app_meta_copy.pop('applicantBag')
                    
                    patent_wrapper.applicationMetaData = ApplicationMetaData(
                        **app_meta_copy,
                        entityStatusData=entity_status,
                        inventorBag=inventor_bag,
                        applicantBag=applicant_bag
                    )
                
                # Parse parent continuity bag
                if 'parentContinuityBag' in wrapper_data:
                    patent_wrapper.parentContinuityBag = [
                        ParentContinuity(**continuity_data) 
                        for continuity_data in wrapper_data['parentContinuityBag']
                    ]
                
                # Parse patent term adjustment data
                if 'patentTermAdjustmentData' in wrapper_data:
                    pta_data = wrapper_data['patentTermAdjustmentData']
                    pta_history_bag = []
                    
                    if 'patentTermAdjustmentHistoryDataBag' in pta_data:
                        pta_history_bag = [
                            PatentTermAdjustmentHistoryData(**history_data)
                            for history_data in pta_data['patentTermAdjustmentHistoryDataBag']
                        ]
                    
                    pta_data_copy = pta_data.copy()
                    if 'patentTermAdjustmentHistoryDataBag' in pta_data_copy:
                        pta_data_copy.pop('patentTermAdjustmentHistoryDataBag')
                    
                    patent_wrapper.patentTermAdjustmentData = PatentTermAdjustmentData(
                        **pta_data_copy,
                        patentTermAdjustmentHistoryDataBag=pta_history_bag
                    )
                
                # Parse assignment bag
                if 'assignmentBag' in wrapper_data:
                    assignments = []
                    for assignment_data in wrapper_data['assignmentBag']:
                        assignors = []
                        if 'assignorBag' in assignment_data:
                            assignors = [
                                Assignor(**assignor_data)
                                for assignor_data in assignment_data['assignorBag']
                            ]
                        
                        assignees = []
                        if 'assigneeBag' in assignment_data:
                            for assignee_data in assignment_data['assigneeBag']:
                                assignee_address = None
                                if 'assigneeAddress' in assignee_data:
                                    assignee_address = AssigneeAddress(**assignee_data['assigneeAddress'])
                                
                                assignees.append(Assignee(
                                    assigneeAddress=assignee_address,
                                    assigneeNameText=assignee_data.get('assigneeNameText')
                                ))
                        
                        correspondence_addresses = []
                        if 'correspondenceAddressBag' in assignment_data:
                            correspondence_addresses = [
                                CorrespondenceAddress(**addr_data)
                                for addr_data in assignment_data['correspondenceAddressBag']
                            ]
                        
                        assignment_data_copy = assignment_data.copy()
                        if 'assignorBag' in assignment_data_copy:
                            assignment_data_copy.pop('assignorBag')
                        if 'assigneeBag' in assignment_data_copy:
                            assignment_data_copy.pop('assigneeBag')
                        if 'correspondenceAddressBag' in assignment_data_copy:
                            assignment_data_copy.pop('correspondenceAddressBag')
                        
                        assignments.append(Assignment(
                            **assignment_data_copy,
                            assignorBag=assignors,
                            assigneeBag=assignees,
                            correspondenceAddressBag=correspondence_addresses
                        ))
                    
                    patent_wrapper.assignmentBag = assignments
                
                # Parse PGPub document metadata
                if 'pgpubDocumentMetaData' in wrapper_data:
                    patent_wrapper.pgpubDocumentMetaData = PGPubDocumentMetaData(
                        **wrapper_data['pgpubDocumentMetaData']
                    )
                
                # Parse child continuity bag
                if 'childContinuityBag' in wrapper_data:
                    patent_wrapper.childContinuityBag = [
                        ChildContinuity(**continuity_data) 
                        for continuity_data in wrapper_data['childContinuityBag']
                    ]
                
                # Parse record attorney
                if 'recordAttorney' in wrapper_data:
                    record_attorney_data = wrapper_data['recordAttorney']
                    power_of_attorney_bag = []
                    
                    if 'powerOfAttorneyBag' in record_attorney_data:
                        for attorney_data in record_attorney_data['powerOfAttorneyBag']:
                            attorney_addresses = []
                            if 'attorneyAddressBag' in attorney_data:
                                attorney_addresses = [
                                    CorrespondenceAddress(**addr_data)
                                    for addr_data in attorney_data['attorneyAddressBag']
                                ]
                            
                            telecom_addresses = []
                            if 'telecommunicationAddressBag' in attorney_data:
                                telecom_addresses = [
                                    TelecommunicationAddress(**telecom_data)
                                    for telecom_data in attorney_data['telecommunicationAddressBag']
                                ]
                            
                            attorney_data_copy = attorney_data.copy()
                            if 'attorneyAddressBag' in attorney_data_copy:
                                attorney_data_copy.pop('attorneyAddressBag')
                            if 'telecommunicationAddressBag' in attorney_data_copy:
                                attorney_data_copy.pop('telecommunicationAddressBag')
                            
                            power_of_attorney_bag.append(Attorney(
                                **attorney_data_copy,
                                attorneyAddressBag=attorney_addresses,
                                telecommunicationAddressBag=telecom_addresses
                            ))
                    
                    customer_number_data = None
                    if 'customerNumberCorrespondenceData' in record_attorney_data:
                        customer_data = record_attorney_data['customerNumberCorrespondenceData']
                        power_of_attorney_addresses = []
                        
                        if 'powerOfAttorneyAddressBag' in customer_data:
                            power_of_attorney_addresses = [
                                CorrespondenceAddress(**addr_data)
                                for addr_data in customer_data['powerOfAttorneyAddressBag']
                            ]
                        
                        customer_number_data = CustomerNumberCorrespondenceData(
                            patronIdentifier=customer_data.get('patronIdentifier'),
                            powerOfAttorneyAddressBag=power_of_attorney_addresses
                        )
                    
                    patent_wrapper.recordAttorney = RecordAttorney(
                        powerOfAttorneyBag=power_of_attorney_bag,
                        customerNumberCorrespondenceData=customer_number_data
                    )
                
                # Parse correspondence address bag
                if 'correspondenceAddressBag' in wrapper_data:
                    patent_wrapper.correspondenceAddressBag = [
                        CorrespondenceAddress(**addr_data)
                        for addr_data in wrapper_data['correspondenceAddressBag']
                    ]
                
                result.patentFileWrapperDataBag.append(patent_wrapper)
        
        return result 