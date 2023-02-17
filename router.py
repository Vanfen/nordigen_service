from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.templating import Jinja2Templates
from starlette.responses import RedirectResponse

from nordigen_service import create_agreement, authenticate, get_institutions, get_results


app_router = APIRouter()

templates = Jinja2Templates(directory="templates")

# Checl if passed argument is HTTPException
def error_check(to_check):
    if type(to_check) == HTTPException and to_check.status_code != 200:
        return True
    else:
        return False

# Countries & banks selection
# if needed to fetch all possible countries and their banks leave country None
# if you specify country in a GET request - only this country banks will be displayed
@app_router.get("/")
async def institutions(request: Request, token: dict=Depends(authenticate), country: str | None = None, error_notification: str | None = None):
    """
    Display countries & institutions to interact with

    Args:
        country (str, optional): if passed only banks available in this country will be fetched
                                 if not passed all countries and banks will be fetched
        error_notification (str, optional): if passed will display its content in the alert box

    Returns:
        Rendering countries.html page with countries/banks available to connect to
    """
    if error_check(token):
        return templates.TemplateResponse("error_display.html", {"request": request, "status_code": token.status_code, "detail": token.detail})
    institutions = await get_institutions(country=country)
    if error_check(institutions):
        return templates.TemplateResponse("error_display.html", {"request": request, "status_code": institutions.status_code, "detail": institutions.detail})
    return templates.TemplateResponse("countries.html", {"request": request, "institutions": institutions, "country": country, "error_notification": error_notification})

# Main page example
@app_router.get("/main")
async def main(request: Request):
    """
    Render main page with choose options:
    Select institutions of a particular coutry or display all posibilities
    """
    return templates.TemplateResponse("main.html", {"request": request})

# Agreements api call to make a successful handshake between user and bank
@app_router.get("/agreements/{institution_id}")
async def agreements(institution_id: str, request: Request):
    """
    Process agreement with passed institution id

    Args:
        institution_id (str): id of the selected institution
        
    Returns:
        Success: Rederecting to the institution authentication page
        HTTPError: Redirects to error page
    """
    if institution_id:
        url = await create_agreement(institution_id, request)
        if error_check(url):
            return templates.TemplateResponse("error_display.html", {"request": request, "status_code": url.status_code, "detail": url.detail})
        return RedirectResponse(url=url)
    
    return RedirectResponse(url="/")

# Results page with all bank information fetched after successful authorization
@app_router.get("/results")
async def results(request: Request):
    """
    Display the fetched data from the institution after successful authorization

    Returns:
        Success: Rederecting to the results page with JSON data fetched
        HTTPError: Redirects to error page
    """
    if "requisition_id" in request.session:
        results = await get_results(request)
        if error_check(results):
            return templates.TemplateResponse("error_display.html", {"request": request, "status_code": results.status_code, "detail": results.detail})
        return results
    error_message = "Authorization to the bank was not made. Try again."
    return RedirectResponse(url=f"/?error_notification={error_message}")
