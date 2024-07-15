# main.py
from contextlib import asynccontextmanager
from typing import Union, Optional, Annotated
from app import settings
from sqlmodel import Field, Session, SQLModel, create_engine, select, Sequence
from fastapi import FastAPI, Depends, HTTPException
from typing import AsyncGenerator
from aiokafka import AIOKafkaProducer, AIOKafkaConsumer
import asyncio
import json
from app import todo_pb2

from app.db_engine import engine
from app.models.product_model import Product
from app.crud.product_crud import add_new_product, get_all_products, get_product_by_id
from app.deps import get_session, get_kafka_producer


def create_db_and_tables() -> None:
    SQLModel.metadata.create_all(engine)


# Kafka Consumer: Consumes messages from Kafka and processes them.
async def consume_messages(topic, bootstrap_servers):
    # Create a consumer instance.
    consumer = AIOKafkaConsumer(
        topic,
        bootstrap_servers=bootstrap_servers,
        group_id="my-product-consumer-group",
    )

    # Start the consumer.
    await consumer.start()
    try:
        # Continuously listen for messages.
        async for message in consumer:
            print("RAW")
            print(f"Received message: {message.value.decode()} on topic {message.topic}")
            
            # Decode and load message data
            product_data = json.loads(message.value.decode())
            print("TYPE", type(product_data))
            print(f"Product Data: {product_data}")
            
            # Save product data to the database
            with next(get_session()) as session:
                print("SAVING DATA TO DATABASE")
                db_insert_product = add_new_product(
                    product_data=Product(**product_data), session=session
                )
                print("DB_INSERT_PRODUCT", db_insert_product)
                # Here you can add code to process each message
                # Example: parse the message, store it in a database
    finally:
        # Ensure to close the consumer when done
        await consumer.stop()


# The first part of the function, before the yield, will

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    print("Creating tables!!...")
    # loop.run_until_complete(consume_messages('todos', 'broker:19092'))
    # task = asyncio.create_task(consume_messages('todos2', 'broker:19092'))
    create_db_and_tables()
    yield


app = FastAPI(
    lifespan=lifespan,
    title="Hello World API with DB",
    version="0.0.1",
)


@app.get("/")
def read_root():
    return {"Hello": "Product Service"}

# @app.post("/manage-products/", response_model=Product)
# async def create_new_product(product: Product, session: Annotated[Session, Depends(get_session)], producer: Annotated[AIOKafkaProducer, Depends(get_kafka_producer)]):
#     product_dict = {field: getattr(product, field) for field in product.dict()}
#     product_json = json.dumps(product_dict).encode("utf-8")
#     print("product_JSON:", product_json)
#     # Produce message
#     await producer.send_and_wait(settings.KAFKA_PRODUCT_TOPIC, product_json)
#     # new_product = add_new_product(product, session)
#     return product


# @app.get("/manage-products/all", response_model=list[Product])
# async def call_all_product(session: Annotated[Session, Depends(get_session)]):
#     """ Create a new product and send it to kafka """
    
#     return get_all_products(session)

# @app.post("/manage-products/{product_id}", response_model=Product)
# def get_single_product(product_id: int, session: Annotated[Session, Depends(get_session)]):
#     """ Get a single product by ID """
    
#     try:
#         return get_product_by_id(product_id=product_id, session=session)
#     except HTTPException as e:
#         raise e
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))
 

# # # Kafka Producer as a dependency




# # # @app.get("/todos/", response_model=list[Todo])
# # # def read_todos(session: Annotated[Session, Depends(get_session)]):
# # #     todos = session.exec(select(Todo)).all()
# # #     return todos