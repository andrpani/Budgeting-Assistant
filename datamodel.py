from pydantic import BaseModel, Field, model_validator
from typing import Optional, List

class Item(BaseModel):
    name: Optional[str] = Field(
        default=None, 
        description="""The name or description of a shopping item found in a receipt. Must be brief, 
                        not including too many details. All other details should go in the info field""")
    unit_price: Optional[float] = Field(
        default=None,
        description="""The price of a single unit of shopping item found in a receipt. If not found, 
                        but the quantity and total price is known, calculate it as total price / quantity"""
    )
    quantity: Optional[int] = Field(
        default=None,
        description="The number of units of the shopping item"
    )
    tot_price: Optional[float] = Field(
        default=None,
        description="""The total price of the shopping item(s). If not found, but the quantity 
                        and the unit price is known, calculate it as unit price * quantity"""
    )
    info: Optional[str] = Field(
        default=None,
        description="Any additional info about the shopping item that would make the name too long"
    )

    @model_validator(mode='after')
    def fill_missing_fields(self) -> "Item":
        if self.quantity and self.tot_price and not self.unit_price:
            self.unit_price = self.tot_price / self.quantity
        if self.quantity and self.unit_price and not self.tot_price:
            self.tot_price = self.unit_price * self.quantity
        if self.unit_price and self.tot_price and not self.quantity:
            self.quantity = self.tot_price / self.unit_price
        
        return self

class Purchase(BaseModel):
    title: Optional[str] = Field(
        default=None,
        description="""A summarizing title for the purchase. Use names of stores
                        shopping-sites and companies"""
    )
    total: Optional[float] = Field(
        default=None,
        description="The total cost of the purchase, considering all the items"
    )
    date: Optional[str] = Field(
        default=None,
        description="The date on which the purchase occured, formatted as DAY/MONTH/YEAR"
    )
    items: List[Item]

class StructuredData(BaseModel):
    purchases: List[Purchase]