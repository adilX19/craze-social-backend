import requests

def verify_tiktok_credentials_and_return_values(username, password):
    flag = False
    user_handle = None

    url = "https://tiktok-all-in-one.p.rapidapi.com/search/user"

    querystring = {"query": username}

    headers = {
        "X-RapidAPI-Host": "tiktok-all-in-one.p.rapidapi.com",
        "X-RapidAPI-Key": "c636fcc6e2msh859242d90e35736p1138e7jsnfa761c38611f"
    }
    response = requests.request("GET", url, headers=headers, params=querystring)

    try:
        json_response = response.json()
        users_list = json_response.get("user_list", [])
        user_handles = [user.get("user_info", {}).get("unique_id", "") for user in users_list]

        for handle in user_handles:
            if handle == username:
                user_handle = handle
                flag = True
                break
    except:
        json_response = {}

    return flag, user_handle