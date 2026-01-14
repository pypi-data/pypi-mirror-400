import logging
import pandas as pd
import requests
import msal
from sharepoint_uploader import SharePointUploader
from execution_logger import ExecutionLogger
from datetime import datetime

tenant_id = 'de50c85b-4591-47e7-a359-8b5bf827b744'
client_id = 'a03c1cf8-2390-41be-9220-66cb233aa030'
client_secret = 'mOP8Q~K4va9yiJ235yIqROZm8SEZez2FB4VByaUN'
scope = 'https://orgcf43c216.api.crm4.dynamics.com/.default'

site_domain_name="thefruitpeople.sharepoint.com"

sp_uploader = SharePointUploader(
    client_id,
    client_secret, 
    tenant_id,
    site_domain_name,
    drive_name="DataInfrastructure-DataLake"
)

app_logger = ExecutionLogger(
    script_name = "Azure_Functions_test",
    client_id=client_id,
    client_secret=client_secret,
    tenant_id=tenant_id,
    sharepoint_url = site_domain_name,
    drive_name= "DataInfrastructure-Logs", 
    folder_path = "Logs/Azure-Functions Test" ,
    
    dv_client_id=client_id ,
    dv_client_secret=client_secret ,
    dv_tenant_id = tenant_id,
    dv_scope = 'https://orgcf43c216.api.crm4.dynamics.com/.default',
    dv_api_url= "https://orgcf43c216.crm4.dynamics.com/api/data/v9.0/cr672_app_errors",
    
)

class InventorySnapshot():
    
    def __init__(self, uploader):
        self.uploader = uploader
    
    def take_snapshot(self):

        app_logger.log_info("get_system_info")
        HEADERS = {
                "Content-Type": "application/json",
                "api-auth-accountid": "297be24b-2c05-4ee0-91dd-deb377d11ea7",
                "api-auth-applicationkey": "66710e6c-0843-10e6-1e78-20e0bf0a9952"
            }

        BASE_URL_PRODUCTS = "https://inventory.dearsystems.com/ExternalApi/v2/product"

        try:
            initial_response = requests.get(f"{BASE_URL_PRODUCTS}?", headers=HEADERS)
            initial_response.raise_for_status()  # Raise exception for 4XX/5XX status codes
            initial_data = initial_response.json()
            total_products = initial_data['Total']
        except requests.exceptions.RequestException as e:
            app_logger.log_error(f"Error in initial API request: {str(e)}")
            return pd.DataFrame()  # Return empty DataFrame on failure
        except (KeyError, ValueError) as e:
            app_logger.log_error(f"Error parsing initial API response: {str(e)}")
            return pd.DataFrame()
        
        # Calculate how many pages we need - DEAR API seems to use a limit of 100 per page
        # Using 100 as default page size based on your sample output
        page_size = 100
        total_pages = -(-total_products // page_size)  # Ceiling division
        
        # print(f"Total products: {total_products}, Total pages: {total_pages}")

        all_data = []
        # Start with the products from the initial request
        all_data.extend(initial_data.get('Products', []))
        
        # Fetch remaining pages
        for page in range(2, total_pages + 1):
            app_logger.log_info(f"Fetching page {page}/{total_pages}")
            page_url = f"{BASE_URL_PRODUCTS}?Page={page}"
            response = requests.get(page_url, headers=HEADERS)
            
            if response.status_code != 200:
                app_logger.log_error(f"Error fetching page {page}: {response.status_code}, {response.text}")
                continue
                
            data = response.json()
            page_products = data.get("Products", [])
            all_data.extend(page_products)
            
            app_logger.log_info(f"Fetched page {page}/{total_pages} with {len(page_products)} products. Total so far: {len(all_data)}/{total_products}")
            app_logger.log_info(f"Fetching page {page}/{total_pages}", "complete")

        print(f"Total products fetched: {len(all_data)}/{total_products}")
        
        df = pd.DataFrame(all_data)
        df = df.rename(columns={
            "AdditionalAttribute4": "Subcategory",
            "AverageCost": "cost",
            "PriceTier1": "price",
            "Name": "Product",
            "StockLocator": "Position"
        })
        
        try:
            parent_folder_path = f"Data Lake/Azure-Functions Test/Snapshots"
            file_name = f"test_snapshot_{datetime.now().strftime('%d-%m-%Y')}"
            sp_uploader.upload_dataframe_as_csv(
                df,  # Use cleaned DataFrame
                file_name + '.csv',
                parent_folder_path
            )
        except Exception as e:
            app_logger.log_error(f"Failed to acquire token","acquire_token",e)
            exit()
        
        # Validation check
        if "Product" not in df.columns:
            app_logger.log_error("'Product' column missing from products DataFrame")
        
        
        app_logger.log_info("get_system_info - completed")
        app_logger.finalize()
    
def main():
    snapshot = InventorySnapshot(sp_uploader)
    snapshot.take_snapshot()
    
    
if __name__ == "__main__":
    main()
        