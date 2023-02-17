from base64 import b64decode
from uuid import uuid4
import os 
from dotenv import load_dotenv
from fastapi import Request
from fastapi.encoders import jsonable_encoder

from nordigen import NordigenClient
import requests
from exceptions import http_exceptions


load_dotenv()

# load secret data from .env file
SECRET_ID = os.getenv("SECRET_ID") 
SECRET_KEY = os.getenv("SECRET_KEY") 

# initialize Nordigen client and pass SECRET_ID and SECRET_KEY
client = NordigenClient(
    secret_id=SECRET_ID,
    secret_key=SECRET_KEY
)

token_data = None
# Create new access and refresh token
# Parameters can be loaded from .env or passed as a string
# Note: access_token is automatically injected to other requests after you successfully obtain it
async def authenticate():
    """
    Authentication in Nordigen

    Raises:
        HTTPException: HTTP error containing data from nordigen api HTTPError

    Returns:
        Received access and reftesh tokens and their lifetime   
    """
    global token_data
    
    try:
        if token_data is not None:
            # Exchange refresh token to new access token
            new_token = client.exchange_token(token_data["refresh"])
            token_data["access"] = new_token["access"]
            token_data["access_expires"] = new_token["access_expires"]
        else:
            # Generating new access token
            token_data = client.generate_token()
        return token_data
    except requests.HTTPError as e:
        return http_exceptions.construct(e)

async def get_institutions(country: str | None = None):
    """
    Get institutions

    Args:
        country (str, optional): if passed only banks available in this country will be fetched
                                 if not passed all countries and banks will be fetched
        
    Raises:
        HTTPException: HTTP error containing data from nordigen api HTTPError

    Returns:
        Institutions fetched from Nordiren        
    """
    try:
        institutions = client.institution.get_institutions(country=country)
        return institutions
    except requests.HTTPError as e:
        return http_exceptions.construct(e)

# # Initialize bank session
async def create_agreement(institution_id: str, request: Request):
    """
    Connect & authenticate user and bank

    Args:
        institution_id (str): id of bank to make agreement with

    Raises:
        HTTPException: HTTP error containing data from nordigen api HTTPError
        
    Returns:
        Redirect link to the bank authentication that matched the passed institution_id
    """
    try:
        init = client.initialize_session(
            # institution id
            institution_id=institution_id,
            # redirect url after successful authentication
            redirect_uri="http://127.0.0.1:8000/results",
            # additional layer of unique ID defined by you
            reference_id=str(uuid4())
        )

        # Get requisition_id and link to initiate authorization process with a bank
        link = init.link # bank authorization link
        requisition_id = init.requisition_id
        request.session["requisition_id"] = requisition_id
        return link
    except requests.HTTPError as e:
        return http_exceptions.construct(e)

async def get_results(request: Request):
    """
    Fetching results from institution after successful authentication
    
    Raises:
        HTTPException: HTTP error containing data from nordigen api HTTPError

    Returns:
        Institution data        
    """
    try:
        accounts = client.requisition.get_requisition_by_id(
            requisition_id=request.session["requisition_id"]
        )["accounts"]

        accounts_data = []
        for id in accounts:
            account = client.account_api(id)
            metadata = account.get_metadata()
            transactions = account.get_transactions()
            details = account.get_details()
            balances = account.get_balances()

            accounts_data.append(
                {
                    "metadata": metadata,
                    "details": details,
                    "balances": balances,
                    "transactions": transactions,
                }
            )

        return jsonable_encoder(accounts_data)
    except requests.HTTPError as e:
        return http_exceptions.construct(e)
    