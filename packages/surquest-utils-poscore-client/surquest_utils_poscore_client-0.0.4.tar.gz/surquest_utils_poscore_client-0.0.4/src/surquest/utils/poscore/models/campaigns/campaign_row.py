from __future__ import annotations
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel

from .partner import Partner
from .brand import Brand
from .carrier import Carrier
from .component import Component
from .campaign_status import CampaignStatus


class CampaignRow(BaseModel):
    id: int
    campaignId: Optional[int] = None
    partnerId: Optional[int] = None
    carrierId: Optional[int] = None
    brandId: Optional[int] = None
    componentId: Optional[int] = None
    partner: Optional[Partner] = None
    brand: Optional[Brand] = None
    carrier: Optional[Carrier] = None
    component: Optional[Component] = None
    campaignStatus: Optional[CampaignStatus] = None
    
    quantity: Optional[int] = None
    locationsCount: Optional[int] = None
    unitPrice: Optional[float] = None
    discount: Optional[float] = None
    totalAmount: Optional[float] = None
    startDate: Optional[datetime] = None
    endDate: Optional[datetime] = None
    modified: Optional[datetime] = None
    
    description: Optional[str] = None
    printComment: Optional[str] = None
    approvalComment: Optional[str] = None
    
    hasInstallationTasks: Optional[bool] = None
    installationDescription: Optional[str] = None
    hasMonitorTasks: Optional[bool] = None
    monitorDescription: Optional[str] = None
    hasDeinstallationTasks: Optional[bool] = None
    deinstallationDescription: Optional[str] = None
    
    deinstalMaterial: Optional[int] = None
    minimumPhotosCount: Optional[int] = None
    productionQuantity: Optional[int] = None
    productionUnitPrice: Optional[float] = None
    productionDiscount: Optional[float] = None
    installationQuantity: Optional[int] = None
    installationUnitPrice: Optional[float] = None
    installationDiscount: Optional[float] = None
    
    realProductionQuantity: Optional[int] = None
    realProductionCost: Optional[float] = None
    realProductionUnitPrice: Optional[float] = None
    
    isProductionUsed: Optional[bool] = None
    isInstallationUsed: Optional[bool] = None
    isInstallationGenerated: Optional[bool] = None
    isMonitorGenerated: Optional[bool] = None
    isDeinstallationGenerated: Optional[bool] = None
    
    priceHistory: Optional[List[dict]] = None
    monitorTaskDates: Optional[List[datetime]] = None
    shopAppBrandName: Optional[str] = None
    ean: Optional[str] = None
    individualName: Optional[str] = None
