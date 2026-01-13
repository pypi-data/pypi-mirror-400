from __future__ import annotations
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field

from .contact import Contact
from .company import Company
from .customer_reference import CustomerReference
from .sales_employee import SalesEmployee
from .campaign_row import CampaignRow
from .campaign_status import CampaignStatus
from .campaign_lock import CampaignLock


class Campaign(BaseModel):
    id: int
    name: str
    pNumber: Optional[str] = Field(None, alias="pNumber")
    created: datetime
    modified: Optional[datetime] = None
    date_from: datetime = Field(..., alias="from")
    date_to: datetime = Field(..., alias="to")
    currency: str
    
    cmContact: Optional[Contact] = None
    company: Optional[Company] = None
    invoiceTo: Optional[CustomerReference] = None
    campaignFrom: Optional[CustomerReference] = None
    amSalesEmployee: Optional[SalesEmployee] = None
    campaignRows: Optional[List[CampaignRow]] = None
    campaignStatus: Optional[CampaignStatus] = None
    campaignLocks: List[CampaignLock]
    
    isYearlyCampaign: Optional[bool] = None
    isCanceled: bool
    cmContactId: int
    companyId: int
    invCustomerId: int
    campCustomerId: int
    amSaleId: int
    invoiceStatus: int
    totalAmount: float
    campaignStatusValue: int
    limigoUseCustomerFrom: bool
    installationProgress: Optional[int] = None
    flags: List[str]
    dunnhumbyId: Optional[int] = None
    retailerAutoApprovalLimit: Optional[int] = None
    useRetailerAutoApproval: bool
    
    # Nullable fields
    cmId: Optional[int] = None
    fxRate: Optional[float] = None
    nextApprovalStep: Optional[str] = None
