import requests
from wordcloud import WordCloud, STOPWORDS
from .models import *
import os
from .db_procedures import (
    save_data_to_instagram_models, 
    save_data_to_tiktok_models
)

from django.conf import settings
from requests.adapters import HTTPAdapter, Retry

def send_request_to_mining_server(flow_name, customer_handle, competitor_handles, timestamp):

    if flow_name == "Instagram":
        url = "http://66.94.109.65/instagram/crazysocial/insights/"
    elif flow_name == "Tiktok":
        url = "http://66.94.109.65/tiktok/crazysocial/insights/"

    response = requests.get(url, params={
        "customer_handle": customer_handle,
        "competitor_handles": ",".join(competitor_handles),
        "timestamp": timestamp,
        "flow_name": flow_name
    })

    try:
        json_response = response.json()
        json_response = json_response.get("dataset", {})
    except:
        json_response = {}

    return json_response


def retrieve_and_save_data_from_backend(request, flow_name, timestamp):
    if request.user.is_authenticated:
        customer = request.user.customer_profile
        competitors = customer.competitors.all()

        if flow_name == "Instagram":
            customer_handle = customer.insta_user_handle
            competitor_handles = [competitor.insta_user_handle for competitor in competitors if '---common---' not in competitor.insta_user_handle]

        elif flow_name == "Tiktok":
            customer_handle = customer.tiktok_user_handle
            competitor_handles = [competitor.tiktok_user_handle for competitor in competitors if '---common---' not in competitor.tiktok_user_handle]

        json_response = send_request_to_mining_server(flow_name, customer_handle, competitor_handles, timestamp)

        if json_response:
            if flow_name == "Instagram":
                save_data_to_instagram_models(request.user.username, json_response, timestamp)
            elif flow_name == "Tiktok":
                save_data_to_tiktok_models(request.user.username, json_response, timestamp)


def get_wordcloud_data(wc_string):
    stopwords_data = set(STOPWORDS) #set(stopwords.words('english'))
    wc_data = {}
    cleaned_data = []

    wc = WordCloud(
        background_color="white", 
        max_words=2000, 
        max_font_size=50,
        stopwords=stopwords_data, 
        contour_width=1, 
        contour_color='steelblue'
    ).generate(wc_string)

    for word, freq in wc.words_.items():
        # only getting words with more than 3 letters
        if len(word) <= 3:  continue

        if wc_data.get(freq, False):    wc_data[freq].append(word)
        else:   wc_data[freq] = [word]

    for freq, words in wc_data.items():
        freq = round(freq, 2)
        if freq < 0.10: continue
        cleaned_data.append({"frequency": freq, "words": words})

    return cleaned_data


def mark_common_competitors_handles(competitors_handles, flow_name, user):
    """
        if a new customer has some profiles same as our previous current customer,
        then we can mark common profile handles, to avoid multiple scrapes...

        # MARK-PATTERN :  handle---common---prevcustomer(django-username)
    """
    marked_competitors_handles = []
    competitors = Competitor.objects.all()

    for competitor_handle in competitors_handles:
        already_common = '---common---' in competitor_handle

        for competitor_object in competitors:
            common_with_mine = competitor_object.customer.django_user == user

            if already_common or common_with_mine: # if already common, leave
                continue

            user_handle = competitor_object.insta_user_handle if flow_name == "Instagram" else competitor_object.tiktok_user_handle

            if user_handle == competitor_handle:
                marked_competitors_handles.append(
                    f"{competitor_handle}---common---{competitor_object.customer.django_user}"
                )
                break
        else:
            marked_competitors_handles.append(competitor_handle)
    
    return marked_competitors_handles


class DataEnrichment():
    def __init__(self):
        self.session = requests.Session()
        retries = Retry(total=5, backoff_factor=1, status_forcelist=[ 502, 503, 504 ])
        self.session.mount('http://', HTTPAdapter(max_retries=retries))

    def extract_geolocation_data(self):
            api_key  = settings.GEO_LOCATION_API_KEY
            api_url  = f"https://ipgeolocation.abstractapi.com/v1/?api_key={api_key}"
            response = requests.get(api_url)

            try:
                json_response = response.json()
            except:
                json_response = {}

            return json_response

    def close_session(self):
        self.session.close()