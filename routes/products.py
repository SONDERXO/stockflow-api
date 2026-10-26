from fastapi import APIRouter, HTTPException
from schemas import ProductCreate, ProductUpdate
from sqlalchemy import text
from database import engine

router = APIRouter(         # Creates a router for product endpoints
    prefix="/products",
    tags=["Products"]
) 

@router.get("/{product_id}")            
def get_product(product_id: int):
    with engine.connect() as connection:
        result = connection.execute(
            text("SELECT * FROM products WHERE id = :product_id"),
            {"product_id": product_id}
        )

        product = result.mappings().first()

        if product:
            return dict(product)
        
    raise HTTPException(
        status_code=404,
        detail="Product not found"
    )

@router.post("/", status_code=201)        
def create_products(product: ProductCreate):
    next_id = max(
            (item["id"] for item in inventory),
            default=0
        ) + 1,
    
    new_product = {
        "id": next_id,
        "name": product.name,
        "price": product.price,
        "stock": product.stock
    }


    inventory.append(new_product)

    return new_product

@router.patch("/{product_id}")            
def update_product(product_id: int, updates: ProductUpdate):
    for product in inventory:
        if product["id"] == product_id:
            update_data = updates.model_dump(
                exclude_unset=True,
                exclude_none=True)
            product.update(update_data)

            return product
        
    raise HTTPException(
        status_code=404,
        detail="Product not found"
    )

@router.delete("/{product_id}")             
def delete_product(product_id: int):
    for product in inventory:
        if product["id"] == product_id:
            inventory.remove(product)
            return {"message": "Product deleted successfully"}

    raise HTTPException(
        status_code=404,
        detail="Product not found"
    )