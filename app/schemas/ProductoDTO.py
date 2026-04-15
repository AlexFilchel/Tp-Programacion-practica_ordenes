from pydantic import BaseModel

class ProductoCreate(BaseModel):
    name:str
    price:float
    
class ProductoRead(BaseModel):
    id:int
    name:str
    price:float