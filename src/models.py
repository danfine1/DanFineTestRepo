from pydantic import BaseModel


class LinkCreate(BaseModel):
    target_url: str


class LinkInfo(BaseModel):
    short_url: str
    short_code: str


class LinkResolveResponse(BaseModel):
    target_url: str


class LinkMonthBreakdownItem(BaseModel):
    month: str
    clicks: int
    earnings: float


class LinkStatsItem(BaseModel):
    short_code: str
    target_url: str
    total_clicks: int
    total_earnings: float
    monthly_breakdown: list[LinkMonthBreakdownItem]
