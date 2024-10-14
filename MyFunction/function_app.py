import azure.functions as func
import logging
from azure.cosmos import CosmosClient, exceptions
import os

# Application settings
database_name = "resume" 
container_name = "counter" 

app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)

@app.route(route="http_triggerbilal")
def http_triggerbilal(req: func.HttpRequest) -> func.HttpResponse:
    # Initialize the Cosmos client here
    cosmos_endpoint = os.getenv("COSMOS_ENDPOINT")
    cosmos_key = os.getenv("COSMOS_KEY")   
    client = CosmosClient(cosmos_endpoint, cosmos_key)
    
    logging.info('Counting a visitor.')

    try:
        # Get the database and container client
        database = client.get_database_client(database_name) 
        container = database.get_container_client(container_name)
        
        # Retrieve the existing visitor count document
        visitor_count_item = container.read_item(item="1", partition_key="1")
        current_count = visitor_count_item['count']
        
        # Increment the count
        new_count = current_count + 1
        
        # Update the document in Cosmos DB
        visitor_count_item['count'] = new_count
        container.upsert_item(visitor_count_item)

        return func.HttpResponse(
            f"Visitor count updated successfully. Current count: {new_count}",
            status_code=200
        )
    except exceptions.CosmosResourceNotFoundError:
        # Handle case where the document does not exist
        initial_count = 1
        new_item = {
            "id": "1",
            "count": initial_count
        }
        container.create_item(body=new_item)
        
        return func.HttpResponse(
            f"Visitor count initialized. Current count: {initial_count}",
            status_code=201
        )
    except Exception as e:
        logging.error(f"Error updating visitor count: {e}")
        return func.HttpResponse(
            "Error updating visitor count.",
            status_code=500
        )
