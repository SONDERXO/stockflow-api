from fastapi import APIRouter, HTTPException, Query
from schemas import ProductCreate, ProductUpdate, StockMovementCreate
from sqlalchemy import text
from database import engine

router = APIRouter(         # Creates a router for product endpoints
    prefix="/products",
    tags=["Products"]
) 

@router.get("/search")
def search_products(search: str):
    search_pattern = f"%{search}%"
    
    with engine.connect() as connection:
        result = connection.execute(
            text("""
                SELECT * FROM products
                WHERE is_active = TRUE
                AND name ILIKE :search
                ORDER BY id ASC
            """),
            {"search": search_pattern}
        )

        searches = result.mappings().all()

        search_list = []
        for product in searches:
            search_list.append(dict(product))

        return search_list


@router.get("/{product_id}")            
def get_product(product_id: int):
    with engine.connect() as connection:
        result = connection.execute(
            text("SELECT * FROM products WHERE id = :product_id AND is_active = TRUE"),
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
            text("SELECT * FROM products WHERE id = :product_id AND is_active = TRUE"),
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
            AND is_active = TRUE
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
    
        UPDATE products
        SET is_active = FALSE
        WHERE id = :product_id
        AND is_active = TRUE
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
        if movement.movement_type == "IN":
            stock_sql = """
                UPDATE products
                SET stock = stock + :quantity
                WHERE id = :product_id
                AND is_active = TRUE
                RETURNING *
            """
        else:
            stock_sql = """
                UPDATE products
                SET stock = stock - :quantity
                WHERE id = :product_id
                AND stock >= :quantity
                AND is_active = TRUE
                RETURNING *
            """

        result = connection.execute(
            text(stock_sql),
            {
                "quantity": movement.quantity,
                "product_id": product_id
            }
        )

        updated_product = result.mappings().first()

        if updated_product is None:
            existing_product = connection.execute(
                text("""
                    SELECT id FROM products
                    WHERE id = :product_id
                    AND is_active = TRUE
                """),
                {"product_id": product_id}
            ).first()

            if existing_product is None:
                raise HTTPException(
                    status_code=404,
                    detail="Product not found"
                )

            raise HTTPException(
                status_code=400,
                detail="Insufficient stock"
            )
        
        movement_result = connection.execute(
            text("""
                INSERT INTO stock_movements
                    (product_id, movement_type, quantity)
                VALUES
                    (:product_id, :movement_type, :quantity)
                RETURNING *
            """),
            {
                "product_id": product_id,
                "movement_type": movement.movement_type,
                "quantity": movement.quantity
            }
        )

        inserted_movement = movement_result.mappings().first()

        return dict(inserted_movement)

@router.get("/{product_id}/movements")
def get_stock_movements(product_id: int):
    with engine.connect() as connection:
        result = connection.execute(
            text("SELECT * FROM products WHERE id = :product_id AND is_active = TRUE"),
            {"product_id": product_id}
        )

        existing_product = result.mappings().first()

        if existing_product is None:
            raise HTTPException(
                status_code=404,
                detail="Product not found"
            )

        get_movement = connection.execute(
            text("""
                SELECT *
                FROM stock_movements
                WHERE id = :product_id
                ORDER BY created_at DESC, id DESC
                """), 
                {"product_id": product_id}
        )

        movements = get_movement.mappings().all()   

        movement_list = []

        for movement in movements:
            movement_list.append(dict(movement))

        return movement_list

@router.get("/")
def get_all_products(
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=10, ge=1, le=100)
):
    offset = (page - 1) * limit
    
    with engine.connect() as connection:
        get_products = connection.execute(
            text("""
                SELECT *
                FROM products
                WHERE is_active = TRUE
                ORDER BY id ASC
                LIMIT :limit OFFSET :offset
                """),
                {
                    "limit": limit,
                    "offset": offset
                }
        )

        products = get_products.mappings().all()

        products_list = []

        for product in products:
            products_list.append(dict(product))

        return products_list