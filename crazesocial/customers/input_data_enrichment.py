from .insta_verifications import verify_instagram_credentials_and_return_values
from .tiktok_verifications import verify_tiktok_credentials_and_return_values
from .utils import mark_common_competitors_handles

def populate_instagram_input(request, username, password, competitors_handles):
    flag, cookies, userhandle = verify_instagram_credentials_and_return_values(username, password)

    if flag:
        # UPDATE INSTA USER CREDENTIALS
        insta_credentials_object = request.user.insta_credentials
        insta_credentials_object.username = username
        insta_credentials_object.password = password
        insta_credentials_object.save()

        # UPDATE USER INSTA COOKIES
        insta_cookies_object = request.user.insta_cookies
        insta_cookies_object.csrftoken = cookies.get("csrftoken", "")
        insta_cookies_object.ds_user_id = cookies.get("ds_user_id", "")
        insta_cookies_object.ig_did = cookies.get("ig_did", "")
        insta_cookies_object.ig_nrcb = cookies.get("ig_nrcb", "")
        insta_cookies_object.mid = cookies.get("mid", "")
        insta_cookies_object.rur = cookies.get("rur", "")
        insta_cookies_object.sessionid = cookies.get("sessionid", "")
        insta_cookies_object.save()

        # UPDATE INSTA USER-HANDLE
        customer_object = request.user.customer_profile
        customer_object.insta_user_handle = userhandle
        customer_object.save()

        # UPDATE INSTA COMPETITORS DATA
        competitors_objects = customer_object.competitors.all()
        # identifies common tiktok competitors handles
        competitors_handles = mark_common_competitors_handles(competitors_handles, "Instagram", request.user)

        for competitor_handle, competitor_object in zip(competitors_handles, competitors_objects):
            if competitor_handle != '':
                competitor_object.insta_user_handle = competitor_handle
                competitor_object.save()

        return {
            "message": "Instagram Credentials verified successfully...",
            "status": "OK" 
        }, 200
    else:
        return {
            "message": "Instagram Credentials verification Failed...",
            "status": "FAILED" 
        }, 400

def populate_tiktok_input(request, username, password, competitors_handles):
    flag, user_handle = verify_tiktok_credentials_and_return_values(username, password)

    if flag:
        # UPDATE TIKTOK USER CREDENTIALS
        tiktok_credentials_object = request.user.tiktok_credentials
        tiktok_credentials_object.username = username
        tiktok_credentials_object.password = password
        tiktok_credentials_object.save()

        # UPDATE INSTA USER-HANDLE
        customer_object = request.user.customer_profile
        customer_object.tiktok_user_handle = user_handle
        customer_object.save()

        # identifies common tiktok competitors handles
        competitors_handles = mark_common_competitors_handles(competitors_handles, "Tiktok", request.user)

        # UPDATE INSTA COMPETITORS DATA
        competitors_objects = customer_object.competitors.all()
        for competitor_handle, competitor_object in zip(competitors_handles, competitors_objects):
            if competitor_handle != '':
                competitor_object.tiktok_user_handle = competitor_handle
                competitor_object.save()

        return {
            "message": "Tiktok Credentials verified successfully...",
            "status": "OK" 
        }, 200
    else:
        return {
            "message": "Tiktok Credentials verification Failed...",
            "status": "FAILED" 
        }, 400