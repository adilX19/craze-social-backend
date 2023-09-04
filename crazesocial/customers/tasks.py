import requests
import time
from celery import shared_task
from .utils import DataEnrichment
from .emails_utils import send_email_notifications

def fetch_and_store_results_to_DB(request, flow_name, username, cust_keyword, comp_keywords, timestamp):
    """
    This function fetches the results from Mining Server.
    Stores the results into Database...
    """

    print("<=========== DATA SAVING PROCEDURE STARTED ===========>")
    print(f"FLOW NAME ===> {flow_name}")

    if flow_name == "Instagram":
        url = f"http://66.94.109.65/instagram/crazysocial/bulk_extraction/check/"
    elif flow_name == "Tiktok":
        url = f"http://66.94.109.65/tiktok/crazysocial/joint_status_check/"

    queries = [cust_keyword] + comp_keywords
    queries = "----".join(queries)

    response = requests.get(url, params={
        "username": username,
        "queries": queries,
        "timestamp": timestamp
    })

    try:
        if response.json().get("status") == True:
            # =========================================
            # FOR DATA SAVING, ON EXTRACTION COMPLETION
            # =========================================

            activity_object = request.user.customer_profile.activities.get(
                django_user=request.user.username, status=False, flow_name=flow_name)
            
            retrieve_and_save_data_from_backend(
                request, 
                activity_object.flow_name,
                activity_object.created
            )

            activity_object.status = True
            activity_object.save()
            print("Data saved successfully...")
            send_email_notifications(username, "abcd@gmail.com")
            print("Saving process completed...")

    except Exception as e:
        print(f"Exception While saving Data: {e}")
    
    print("<=========== DATA SAVING TASK COMPLETED ==============>")

def crazysocial_crawler(username, keyword, timestamp, flow_name):
    # ================================================================
    # URLS & THEIR QUERY PARAMETERs TO SEND WITH EACH REQUEST..
    # ================================================================

    if flow_name == "Instagram":
        ext_url    = "http://66.94.109.65/instagram/extract_profile_data/"
        ext_params = {
            'keyword': keyword,
            'username': username,
            'timestamp': timestamp,
            'insta_csrftoken': 'XvTBYKT93MSpSK8jHhyCDc8ygnaCzaKo',
            'insta_ds_user_id': '53166775383',
            'insta_ig_did': 'C5DED21D-83FD-43CD-B398-14B37B31B457',
            'insta_ig_nrcb': '1',
            'insta_mid': 'YihBuAALAAE5jK7MhHjTNFiFNH8D',
            'insta_rur': 'RVA\05453166775383\0541684950580:01f7c42c2b3ea602bdedda85109e48bf845d9888e87d803bf62a0666eae2f1643d05bba9',
            'insta_sessionid': '53166775383%3AfYjGvhCRZSfpZ7%3A8',
        }
    elif flow_name == "Tiktok":
        videos_count = 20
        ext_url = f"http://66.94.109.65/tiktok/extract_profile/{timestamp}/{username}/{keyword}/{videos_count}/"
        ext_params = {}

    try:
        response = requests.get(ext_url, params=ext_params)
        print("STATUS ==> ", response.status_code)
        json_response = response.json()
    except Exception as e:
        print("EXCEPTION ==> ", e)

    if json_response['task_created']:
        print("Task created successfully...")

@shared_task(bind=True)
def social_extraction_join_task(self, username, cust_keyword, comp_keywords, timestamp, flow_name, request):
    print("<======= INPUT DATA =======>")
    print("Username ==> ", username)
    print("Customer ==> ", cust_keyword)
    print("Competitor ==> ", comp_keywords)
    print("Timestamp ==> ", timestamp)

    """
        We have to run 5 extractions.
        1 for customer profile.
        4 for our competitors profiles.

        To prevent Database lock, we'll run the extraction
        with wait of 180 seconds approx 3 minutes gap...
    """

    wait_time = 180 if flow_name == "Instagram" else 100

    crazysocial_crawler(username, cust_keyword, timestamp, flow_name)

    for comp_keyword in comp_keywords:
        time.sleep(wait_time)
        crazysocial_crawler(username, comp_keyword, timestamp, flow_name)

    # fetch_and_store_results_to_DB(request, flow_name, username, cust_keyword, comp_keywords, timestamp)

# USER LOCATION DATA ENRICHMENT DURING FIRST TIME SIGNUP PROCESS...
@shared_task(bind=True)
def data_enrichment_task(self, user):
    data_enrichment = DataEnrichment()
    geolocation_data = data_enrichment.extract_geolocation_data()

    if geolocation_data:

        user.region       = geolocation_data.get("region")
        user.country      = geolocation_data.get("country")
        user.country_code = geolocation_data.get("country_code")
        user.city         = geolocation_data.get("city")
        user.continent    = geolocation_data.get("continent")
        user.latitude     = geolocation_data.get("latitude")
        user.longitude    = geolocation_data.get("longitude")

        user.save()
            
    data_enrichment.close_session()
    print("Data Enrichment done successfully...")