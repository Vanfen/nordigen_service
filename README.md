# Nordigen services usage

By using this project you will be able to:
  - Authenticate to Nordigen
  - List all institutions supported by Nordigen
  - Create the user-bank agreement to be able to read data from the institution
  - Fetch the available data from the connected institution

## Requirements

1. For the development was used Python 3.11.0
2. It needed to:
   + Register in ob.nordigen.com;
   + Setup access tokens;

## How to run the project

  1. **Optional, but suggested**
     + Create a virtual env: `python -m venv [NAME OF VM]`
     + Run venv `[NAME OF VM]\Scripts\activate`
  2. Install all required libraries:  `pip install -r requirements.txt`
  3. Create *.env* file with following content:
     ```
     SECRET_ID = [SECRET_ID from ob.nordigen.com]
     SECRET_KEY = [SECRET_KEY from ob.nordigen.com]
     ```
  4. Run the local server: `uvicorn app:app --reload`
  5. Access the local server at 127.0.0.1:8000/main

#### Please find below Nordigen documentation that can help:

+ https://nordigen.com/en/account_information_documenation/api-documention/overview/
+ https://nordigen.com/en/account_information_documenation/integration/quickstart_guide/
