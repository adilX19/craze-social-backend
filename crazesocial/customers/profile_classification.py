import requests

def normalize_formats_to_numbers(value):
    if 'M' in value:
        value = value.replace('M', '')
        value = float(value) * 1000000
    elif 'K' in value:
        value = value.replace('K', '')
        value = float(value) * 1000
    return float(value)

def identify_influencer_class(followers):
    influencer_class = ''

    if followers >= 1000000:
        influencer_class = "Mega"
    elif followers >= 500000 and followers < 1000000:
        influencer_class = "Macro"
    elif followers >= 50000 and followers < 500000:
        influencer_class = "Mid-tier"
    elif followers >= 10000 and followers < 50000:
        influencer_class = "Micro"
    elif followers >= 3000 and followers < 10000:
        influencer_class = "Nano"
    else:
        influencer_class = "Non-Influencer"
    
    return influencer_class

def classify_insta_profile(post_engagement, reels_engagement, followers, flow_name):

    followers = normalize_formats_to_numbers(followers) if flow_name == "Tiktok" else int(followers)

    influencer_class = identify_influencer_class(followers)
    indicator = ""

    if flow_name == "Instagram":
        if post_engagement > 1.0 or reels_engagement > 1.0:
            if post_engagement > reels_engagement:
                indicator = "Posts Driven"
            elif reels_engagement > post_engagement:
                indicator = "Reels Driven"

    elif flow_name == "Tiktok" and post_engagement > 5.0:
        indicator = "Posts Driven"

    if indicator:
        classification = f"{influencer_class} ({indicator})"
    else:
        classification = f"{influencer_class}"
        
    return classification


# CODE FOR MONTHLY ENGAGEMENT OF JOINT TIKTOK AND INSTAGRAM ON DASHBOARD
def finalize_monthly_engagement(engagements_data, flow, flow_engagement):

    engagements_months = [flow_eng["month"] for flow_eng in flow_engagement]

    final_data = {
        "name": flow,
        "data": [0.0] * len(engagements_data["categories"])
    }

    for month in engagements_data["categories"]:
        eng_value = 0.0

        if month in engagements_months:
            for eng in flow_engagement:
                if eng.get("month") == month:
                    eng_value = eng.get("engagement")
                    break

            final_data["data"][engagements_data["categories"].index(month)] = eng_value

    return final_data

def get_dashboard_monthly_engagement(customer):
    try:
        instagram_engagement = requests.get(
            "http://66.94.109.65/instagram/monthly_engagement/",
            params={"customer": customer.insta_user_handle}
        ).json().get("monthly_engagement_instagram")
    except:
        instagram_engagement = []

    try:
        tiktok_engagement = requests.get(
            "http://66.94.109.65/tiktok/monthly_engagement/",
            params={"customer": customer.tiktok_user_handle}
        ).json().get("monthly_engagement_tiktok")
    except:
        tiktok_engagement = []

    engagements_data = {
        "categories": ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
        "data": []
    }

    engagements_data["data"].append(
        finalize_monthly_engagement(engagements_data, "Instagram", instagram_engagement)
    )

    engagements_data["data"].append(
        finalize_monthly_engagement(engagements_data, "Tiktok", tiktok_engagement)
    )

    return engagements_data

def get_social_evolution_data(monthly_engagements):
    result = {
        "categories": ["Jan", "Feb", "Mar", "Apr", "May", "Jun"],
        "data": []
    }

    data = []

    instagram_engagements = monthly_engagements.get("data", [''])[0].get("data", [])
    tiktok_engagements = monthly_engagements.get("data", [''])[1].get("data", [])


    for inst_eng, tik_eng in zip(instagram_engagements, tiktok_engagements):
        data.append(inst_eng + tik_eng)


    for i in range(len(data)):

        try:
            first = data[i]
            second = data[i+1]
            res = ((second - first) / first) * 100
        except:
            res = 0.0

        if res < 0:
            res = -1 * res

        if int(res) >= 100:
            res = 0.0

        data[i] = round(res, 1)

    result["data"].append({
        'name': 'insta_tiktok',
        'data': data
    })
    return result