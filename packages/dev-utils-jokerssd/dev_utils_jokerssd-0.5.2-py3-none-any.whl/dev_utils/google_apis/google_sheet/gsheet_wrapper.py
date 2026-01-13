from pydantic import EmailStr
from pydantic_gsheets import SheetRow, get_sheets_service, AuthConfig, AuthMethod, GoogleWorkSheet,GSRequired,GSReadonly
from typing import Annotated

YOUR_SHEET_ID = "12412412412412"
YOUR_SHEET_NAME = ""

class Customer(SheetRow):
    name: Annotated[str,GSRequired(),GSReadonly()]
    email: Annotated[EmailStr,GSRequired()]
    age: Annotated[int,GSRequired()]

svc = get_sheets_service(AuthConfig( #Use your personal auth, this is a helper for oauth
    method=AuthMethod.USER_OAUTH,
    client_secrets_file="/Users/jokerssd/.config/gspread/credentials.json",
    token_cache_file="/Users/jokerssd/.config/gspread/token.json",
))

# Connect to a Google Sheet worksheet
ws = GoogleWorkSheet.create_sheet(
    Customer,
    svc,
    "{YOUR_SHEET_ID}",
    "{YOUR_SHEET_NAME}",
    skip_if_exists=True, #skip if sheet exists, defaults to True
    )

row1 = Customer(name="Alice", email="alice@example.com", age=30,)
ws.saveRow(row1)

# Load data into Python
customers = list(ws.rows()) # Dequeue as rows() returns a generator
print(customers)