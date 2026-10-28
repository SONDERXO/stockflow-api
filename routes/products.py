from fastapi import APIRouter, HTTPException
from schemas import ProductCreate, ProductUpdate, StockMovementCreate
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
    query = text("""
        INSERT INTO products (name, price, stock)
        VALUES (:name, :price, :stock)
        RETURNING *
    """) 

    with engine.begin() as connection:
        result = connection.execute(
            query,
            {
                "name": product.name,
                "price": product.price,
                "stock": product.stock
            }
        )

        new_product = result.mappings().first()

    return dict(new_product)


@router.patch("/{product_id}")
def update_product(product_id: int, updates: ProductUpdate):
    with engine.begin() as connection:
        result = connection.execute(
            text("SELECT * FROM products WHERE id = :product_id"),
            {"product_id": product_id}
        )

        existing_product = result.mappings().first()

        if existing_product is None:
             raise HTTPException(
                        status_code=404,
                        detail="Product not found"
                    )
        
        product_data = dict(existing_product)        
        
        update_data = updates.model_dump(
            exclude_unset=True,
            exclude_none=True
        )

        product_data.update(update_data)

        query = text("""
            UPDATE products
            SET name = :name,
                price = :price,
                stock = :stock
            WHERE id = :product_id
            RETURNING *
        """)

        result = connection.execute(
            query,
            {
                "name": product_data["name"],
                "price": product_data["price"],
                "stock": product_data["stock"],
                "product_id": product_data["id"]
            }
        )

        updated_product = result.mappings().first()

        return updated_product


@router.delete("/{product_id}")
def delete_product(product_id: int):
    query = text("""
        DELETE FROM products
        WHERE id = :product_id
        RETURNING *
    """)

    with engine.begin() as connection:
        result = connection.execute(
            query, {"product_id": product_id}
        )

        deleted_product = result.mappings().first()

    if deleted_product is None:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )

    return dict(deleted_product)


@router.post("/{product_id}/movements", status_code=201)
def create_stock_movement(product_id: int, movement: StockMovementCreate):
    with engine.begin() as connection:
        result = connection.execute(
            text("""
                UPDATE products
                SET stock = stock + :quantity
                WHERE id = :product_id
                RETURNING *
            """),
            {
                "quantity": movement.quantity,
                "product_id": product_id
            }
        )

        updated_product = result.mappings().first()

        if updated_product is None:
            raise HTTPException(
                status_code=404,
                detail="Product not found"
            )

        
