from fastapi import HTTPException
from sqlmodel import Session, select
from app.models.product_model import Product, ProductUpdate
from app.db_engine import engine


# Add a New Product to the Database
def add_new_product(product_data: Product, session: Session):
    print("Adding Product to Database")
    session.add(product_data)
    session.commit()
    session.refresh(product_data)
    return product_data

# Get All Products from the Database
def get_all_products(session: Session):
    all_products = session.exec(select(Product)).all()
    return all_products

# Get A Product by ID 
def get_product_by_id(product_id:int, session: Session):
    product = session.exec(select(Product)).where(Product.id == product_id).one_or_none()
    if product is None:
        raise HTTPException(status_code=404, detail = "Product not found")
    return product
    
# Delete Product by ID 
def delete_product_by_id(product_id:int, session: Session):
    # Get A Product by ID 
    product = session.exec(select(Product)).where(Product.id == product_id).one_or_none()
    if product is None:
        raise HTTPException(status_code=404, detail = "Product not found")
    # Step 02 : Delete the product
    session.delete(product)
    session.commit()
    return {"message": "Product Deleted Successfully"}

def update_product_by_id(product_id: int, to_update_product_data:ProductUpdate, session: Session):
    # Step 1: Get the Product by ID
    product = session.exec(select(Product).where(Product.id == product_id)).one_or_none()
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    # Step 2: Update the Product
    hero_data = to_update_product_data.model_dump(exclude_unset=True)
    product.sqlmodel_update(hero_data)
    # db_product.name = product.name
    # db_product.category = product.category
    # db_product.description = product.description
    # db_product.price = product.price
    # db_product.stock = product.stock
    # db_product.image_url = product.image_url
    session.add(product)
    session.commit()
    session.refresh(product)
    return product
    
# Validate Product by ID 
def validate_product(product_id:int, session: Session) -> Product | None :
    product = session.exec(select(Product)).where(Product.id == product_id).one_or_none()
    if product is None:
        raise HTTPException(status_code=404, detail = "Product not found")
    return product    