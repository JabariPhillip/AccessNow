from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field

class ReviewCreate(BaseModel):
    user_id: int
    rating: int = Field(ge=1, le=5)
    category: str
    body: str = Field(min_length=1, max_length=2000)

class ReviewOut(BaseModel):
    id: int
    rating: int
    category: str
    body: str
    author: str
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class AccessibilityOut(BaseModel):
    category: str
    description: str
    percent: int
    model_config = ConfigDict(from_attributes=True)

class VenueListOut(BaseModel):
    id: int
    name: str
    address: str
    type: str
    icon: str
    verified: str
    score: int
    review_count: int
    tags: list[str]
    map_x: float
    map_y: float

class VenueOut(VenueListOut):
    accessibility: list[AccessibilityOut]
    latest_review: ReviewOut | None

class UserOut(BaseModel):
    id: int
    name: str
    role: str
    review_count: int
    model_config = ConfigDict(from_attributes=True)

class SavedCreate(BaseModel):
    user_id: int
    venue_id: int

class SavedOut(BaseModel):
    id: int
    venue: VenueListOut

class RouteOut(BaseModel):
    venue_name: str
    minutes: int
    miles: float
    alternative_minutes: int
    alternative_miles: float
    alert: str
