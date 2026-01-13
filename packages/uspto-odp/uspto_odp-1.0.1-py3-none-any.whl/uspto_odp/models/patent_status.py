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
try:
    from enum import StrEnum  # Python 3.11+
except ImportError:
    from strenum import StrEnum  # Python <3.11

class ApplicationStatus(StrEnum):
    """USPTO Application Status Codes and Descriptions"""
    MISASSIGNED = "1"  # Misassigned Application Number
    SENT_TO_CLASSIFICATION = "17"  # Sent to Classification contractor
    RETURNED_TO_PREEXAM = "18"  # Application Returned back to Preexam
    PREEXAM_PROCESSING = "19"  # Application Undergoing Preexam Processing
    DISPATCHED_FROM_PREEXAM = "20"  # Application Dispatched from Preexam, Not Yet Docketed
    DOCKETED_NEW_CASE = "30"  # Docketed New Case - Ready for Examination
    AWAITING_RESPONSE = "31"  # Awaiting response for informality, fee deficiency or CRF action
    SPECIAL_NEW = "37"  # Special New
    NON_FINAL_COUNTED = "40"  # Non Final Action Counted, Not Yet Mailed
    NON_FINAL_MAILED = "41"  # Non Final Action Mailed
    QUAYLE_COUNTED = "50"  # Ex parte Quayle Action Counted, Not Yet Mailed
    QUAYLE_MAILED = "51"  # Ex parte Quayle Action Mailed
    FINAL_REJECTION_COUNTED = "60"  # Final Rejection Counted, Not Yet Mailed
    FINAL_REJECTION_MAILED = "61"  # Final Rejection Mailed
    WITHDRAWN_ABANDONMENT = "66"  # Withdrawn Abandonment, awaiting examiner action
    RESPONSE_AFTER_FINAL = "80"  # Response after Final Action Forwarded to Examiner
    ADVISORY_ACTION_COUNTED = "82"  # Advisory Action Counted, Not Yet Mailed
    ADVISORY_ACTION_MAILED = "83"  # Advisory Action Mailed
    ALLOWED_NOTICE_PENDING = "90"  # Allowed -- Notice of Allowance Not Yet Mailed
    WITHDRAW_FROM_ISSUE = "91"  # Withdraw from issue awaiting action
    NOTICE_OF_ALLOWANCE_MAILED = "93"  # Notice of Allowance Mailed -- Application Received in Office of Publications
    ISSUE_FEE_RECEIVED = "94"  # Publications -- Issue Fee Payment Received
    ISSUE_FEE_VERIFIED = "95"  # Publications -- Issue Fee Payment Verified
    AWAITING_TC_NO_FEE = "98"  # Awaiting TC Resp., Issue Fee Not Paid
    AWAITING_TC_FEE_RECEIVED = "99"  # Awaiting TC Resp, Issue Fee Payment Received
    AWAITING_TC_FEE_VERIFIED = "100"  # Awaiting TC Resp, Issue Fee Payment Verified
    APPEAL_READY = "116"  # Appeal Ready for Review
    TC_RETURN_OF_APPEAL = "119"  # TC Return of Appeal
    NOTICE_OF_APPEAL = "120"  # Notice of Appeal Filed
    EXAMINERS_ANSWER_COUNTED = "122"  # Examiner's Answer to Appeal Brief Counted
    EXAMINERS_ANSWER_MAILED = "123"  # Examiner's Answer to Appeal Brief Mailed
    APPEAL_PENDING = "124"  # On Appeal -- Awaiting Decision by the Board of Appeals
    REMAND_TO_EXAMINER = "125"  # Remand to Examiner from Board of Appeals
    AMENDMENT_AFTER_APPEAL = "127"  # Amendment after notice of appeal
    EXAMINERS_ANSWER_TO_REPLY = "130"  # Examiner's Answer to Reply Brief or Response to Remand Mailed
    BOARD_DECISION = "135"  # Board of Appeals Decision Rendered
    AMENDMENT_AFTER_BOARD = "136"  # Amendment / Argument after Board of Appeals Decision
    PROSECUTION_SUSPENDED = "140"  # Prosecution Suspended
    REQUEST_RECONSIDERATION = "143"  # Request Reconsideration after Board of Appeals Decision
    PATENTED = "150"  # Patented Case
    PATENTED_OLD_CASE = "151"  # Patented File - (Old Case Added for File Tracking Purposes)
    PROVISIONAL_EXPIRED = "159"  # Provisional Application Expired
    ABANDONED_INCOMPLETE = "160"  # Abandoned -- Incomplete Application (Pre-examination)
    ABANDONED_NO_RESPONSE = "161"  # Abandoned -- Failure to Respond to an Office Action
    ABANDONED_DURING_PUBLICATION = "162"  # Expressly Abandoned -- During Publication Process
    ABANDONED_AFTER_APPEAL = "163"  # Abandoned -- After Examiner's Answer or Board of Appeals Decision
    ABANDONED_NO_ISSUE_FEE = "164"  # Abandoned -- Failure to Pay Issue Fee
    ABANDONED_RESTORED = "165"  # Abandoned - Restored
    ABANDONED_FWC_PARENT = "166"  # Abandoned -- File-Wrapper-Continuation Parent Application
    ABANDONED_DRAWINGS = "167"  # Abandonment for Failure to Correct Drawings/Oath/NonPub Request
    ABANDONED_DURING_EXAMINATION = "168"  # Expressly Abandoned -- During Examination
    RENOUNCED = "170"  # Renounced-International design application designating the U.S. renounced under the Hague Agreement
    INTERFERENCE_DECLARED = "174"  # Interference -- Declared by Board of Interferences
    COURT_PROCEEDINGS = "195"  # Application Involved in Court Proceedings
    COURT_PROCEEDINGS_TERMINATED = "197"  # Court Proceedings Terminated
    PATENT_EXPIRED = "250"  # Patent Expired Due to Non Payment of Maintenance Fees Under 37 CFR 1.362
    PRE_INTERVIEW_MAILED = "311"  # Pre-Interview Communication Mailed
    REEXAM_INCOMPLETE = "408"  # Incomplete Ex Parte Reexam (Filing Date Vacated)
    REEXAM_ASSIGNED = "412"  # Reexam Assigned to Examiner for Determination
    REEXAM_ORDERED = "414"  # Determination - Reexamination Ordered
    REEXAM_DENIED = "416"  # Request for Reexamination Denied
    REEXAM_PETITION = "418"  # Petition Received RE: Denial of Reexamination Request
    REEXAM_TERMINATED_GROUP = "420"  # Reexam Terminated -- Request Denied in Group
    REEXAM_TERMINATED_DECISION = "421"  # REEXAM TERMINATED - Decision
    REEXAM_TERMINATED_VACATED = "422"  # Reexam Terminated -- Previous Order Vacated
    REEXAM_NON_FINAL = "423"  # Non-Final Action Mailed
    REEXAM_RESPONSE = "424"  # Response after Non-Final Action Entered (or Ready for Examiner Action)
    REEXAM_FINAL = "425"  # Final Action Mailed
    REEXAM_RESPONSE_FINAL = "426"  # Response after Final Action Received
    REEXAM_APPEAL_WITHDRAWN = "427"  # Withdrawal / Dismissal of Appeal
    REEXAM_ADVISORY = "428"  # Advisory Action Mailed
    REEXAM_SUSPENDED = "429"  # Reexamination Suspended
    REEXAM_APPEAL = "432"  # Notice of Appeal Filed
    REEXAM_APPEAL_BRIEF = "433"  # Appeal Brief Filed (or Remand from Board) - Awaiting Examiner Action
    REEXAM_EXAMINER_ANSWER = "435"  # Examiner's Answer Mailed
    REEXAM_EX_PARTE = "436"  # Reexam -- Request Ready for Ex Parte Action
    REEXAM_REPLY_BRIEF = "437"  # Reply Brief Filed
    REEXAM_BOARD_DECISION = "440"  # Decision on Appeal Rendered by Board
    REEXAM_RECONSIDERATION = "441"  # Request for Reconsideration after BPAI Decision
    REEXAM_BPAI_FINAL = "444"  # BPAI decision on rehearing - Decision is final and appealable
    REEXAM_CAFC_REMAND = "445"  # CAFC Decision Remanded to PTAB
    REEXAM_CERTIFICATE_INTENT = "450"  # Reexam Terminated -- Notice of Intent to Issue a Reexamination Certificate Mailed
    REEXAM_CERTIFICATE_PUBLICATION = "452"  # Reexam Terminated -- In Publications for Issue of a Certificate
    REEXAM_CERTIFICATE_ISSUED = "454"  # Reexamination Certificate Issued
    SE_READY_PUBS = "650"  # SE ready for Pubs Processing -- Certificate in IFW
    SE_FORWARDED = "652"  # Supplemental Examination Forwarded to Pubs (NO SNQ)
    REEXAM_READY = "660"  # Ready for Reexam -- Certificate in IFW
    SE_CERTIFICATE_INTENT = "670"  # Intent to Issue Certificate based on Supplemental Exam
    SE_CERTIFICATE = "680"  # Reexamination SE Certificate
    INTER_PARTES_TERMINATED = "809"  # Preprocessing Terminated--Inter Partes Reexam
    REEXAM_REQUEST_DENIED = "816"  # Request for reexamination denied
    REEXAM_PETITION_RECEIVED = "818"  # Petition received re: Denial of a request for reexamination
    REEXAM_PETITION_DENIED = "820"  # Decision on Petition Denied, Reexam Request Denied, Terminated
    REEXAM_VACATED = "822"  # Decision vacating reexam
    NON_FINAL_ACTION = "823"  # Non-final action mailed
    RESPONSE_TIMELY = "825"  # Response after non-final action - owner - timely
    READY_AFTER_RESPONSE = "827"  # Ready for examiner action after response/comments after nonfinal
    READY_AFTER_COMMENTS = "837"  # Ready for examiner action after owner/requester comments periods after ACP
    REEXAM_CERTIFICATE_INTENT_IP = "850"  # Notice of Intent to Issue Reexam Certificate
    REEXAM_CERTIFICATE_ISSUED_IP = "854"  # Reexamination Certificate issued
    READY_AFTER_BRIEFS = "857"  # Ready for examiner action after owner/requester N/AP and appropriate briefs
    ORAL_HEARING = "871"  # Oral hearing request - requester

class ApplicationStatusDerived(StrEnum):
    """Derived/simplified USPTO Application Status categories"""
    UNKNOWN = "UNKNOWN"
    PENDING = "PENDING"    # Application is still active/in process
    MAYBE_PENDING = "MAYBE_PENDING" # Application may be pending, but we don't have enough information to know for sure (maybe)
    ALLOWED = "ALLOWED" # Application has been allowed
    ABANDONED = "ABANDONED"  # Application has been abandoned
    MAYBE_ABANDONED = "MAYBE_ABANDONED" # Application may be abandoned, but we don't have enough information to know for sure (maybe)
    EXPIRED = "EXPIRED"    # Application or patent has expired
