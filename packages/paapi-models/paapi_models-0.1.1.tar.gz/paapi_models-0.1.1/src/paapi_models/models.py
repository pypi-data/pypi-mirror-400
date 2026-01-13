from pydantic import BaseModel


class VinylModel(BaseModel):
    asin: str
    url: str
    title: str
    release_date: str
    merchant: str
    availability: str
    price_amount: float
    price_display_amount: str
    savings_amount: float
    savings_display_amount: str
    savings_percentage: float
    images_primary: dict
    images_variants: list[dict]
    sales_rank: int
    barcodes: list[str]
    artists: list[str]
    genres: list[str]
    styles: list[str]
    labels: list[str]
