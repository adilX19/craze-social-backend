from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
from customers.models import UserActivity
import requests
from customers.utils import get_wordcloud_data, retrieve_and_save_data_from_backend
from customers.profile_classification import classify_insta_profile
from django.forms.models import model_to_dict

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from customers.profile_classification import normalize_formats_to_numbers

from .models import *

from .utils import (
    get_best_monthly_engagement_data, 
    get_monthly_interations_data, 
    get_weekly_distribution_of_data
)

def home_page(request):
    name = 'Tiktok'
    return render(request, 'tiktok.html', {'name': name})

def tiktok_extraction_data(request):
    search_activity = UserActivity.objects.filter(django_user=request.user.username, flow_name='Tiktok').last()
    
    response = requests.get('http://66.94.109.65/tiktok/crazysocial/insights/', params={
        "customer_handle": search_activity.customer_handle,
        "competitor_handles": search_activity.competitors, 
        "timestamp": search_activity.created
    })

    data = response.json()

    # customer wordcloud data
    customer_data = data["dataset"]["customer_dataset"]
    # customer_data["wordcloud_data"] = get_wordcloud_data(customer_data["wordcloud_data"])

    customer_data["profile_data"]["class"] = classify_insta_profile(
        customer_data.get("insights_data", {}).get("post_engagement", 0.0),
        customer_data.get("insights_data", {}).get("reels_engagement", 0.0),
        customer_data.get("profile_data", {}).get("followers", 0),
        search_activity.flow_name
    )

    # competitors wordcloud data
    for competitor_dataset in data["dataset"]["competitors_dataset"]:
        # competitor_dataset["wordcloud_data"] = get_wordcloud_data(competitor_dataset["wordcloud_data"])

        competitor_dataset["profile_data"]["class"] = classify_insta_profile(
            competitor_dataset.get("insights_data", {}).get("post_engagement", 0.0),
            competitor_dataset.get("insights_data", {}).get("reels_engagement", 0.0),
            competitor_dataset.get("profile_data", {}).get("followers", 0),
            search_activity.flow_name
        )

    return JsonResponse(data)

def tiktok_data_save_db(request):
    
    activity_object = UserActivity.objects.filter(flow_name='Tiktok').first()

    retrieve_and_save_data_from_backend(
        request, 
        activity_object.flow_name,
        activity_object.created
    )
    return HttpResponse(f"<h1>Data saved to {activity_object.flow_name} Models Successfully...</h1>")

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def tiktok_data_response(request):
    competitors_data_list = []

    best_monthly_engagement_data = []
    best_weekly_engagement_data = []

    monthly_interactions_data = []
    weekly_interactions_data = []

    search_activity = UserActivity.objects.filter(django_user=request.user.username, flow_name='Tiktok').last()

    # CUSTOMER DATA FETCHING FROM DATABASE...
    customer_profile = TiktokUserProfile.objects.get(
        tiktok_userhandle=search_activity.customer_handle,
        created=search_activity.created
    )
    customer_insights = TiktokProfileInsights.objects.get(
        tiktok_userhandle=search_activity.customer_handle,
        created=search_activity.created
    )
    customer_top_hashtags = customer_profile.hashtags.all()
    customer_total_hashtags_posts = sum([int(hashtag.item_count) for hashtag in customer_profile.hashtags.all()])
    customer_top_hashtags = [model_to_dict(hashtag_object) for hashtag_object in customer_top_hashtags]
    customer_wordcloud_data = get_wordcloud_data(customer_profile.wordcloud_string)
    # ===================================================================================


    # COMPETITORS DATA FETCHING FROM DATABASE...
    comp_handles_join = search_activity.competitors.split(',')

    if search_activity.common_profiles != '':
        comp_handles_join = comp_handles_join + search_activity.common_profiles.split(',')

    minging_server_competitors_handles = []

    for competitor_handle in comp_handles_join:

        if '---common---' in competitor_handle:
            common_search_activity = UserActivity.objects.filter(
                django_user=competitor_handle.split('---')[-1], flow_name='Tiktok').last()
            created = common_search_activity.created
            competitor_handle = competitor_handle.split('---')[0]
        else:
            created = search_activity.created
        

        competitor_profile = TiktokUserProfile.objects.get(
            tiktok_userhandle=competitor_handle,
            created=created
        )
        
        competitor_insights = TiktokProfileInsights.objects.get(
            tiktok_userhandle=competitor_handle,
            created=created
        )

        minging_server_competitors_handles.append(competitor_handle)

        competitor_top_hashtags = competitor_profile.hashtags.all()
        competitor_total_hashtags_posts = sum([int(hashtag.item_count) for hashtag in competitor_profile.hashtags.all()])
        competitor_top_hashtags = [model_to_dict(hashtag_object) for hashtag_object in competitor_top_hashtags]
        competitor_wordcloud_data = get_wordcloud_data(competitor_profile.wordcloud_string)
        
        competitor_profile = model_to_dict(competitor_profile)
        del competitor_profile["wordcloud_string"]
        
        competitors_data_list.append({
            'profile_data': competitor_profile,
            'insights_data': model_to_dict(competitor_insights),
            'top_hashtags': competitor_top_hashtags,
            'total_hashtag_posts': competitor_total_hashtags_posts,
            "wordcloud_data": competitor_wordcloud_data
        })
    # ===================================================================================

    customer_profile = model_to_dict(customer_profile)
    del customer_profile["wordcloud_string"]

    # CUSTOMER INSTA ANALYTICS FROM MINING SERVER...
    try:
        mining_response = requests.get("http://66.94.109.65/tiktok/profile_analytics/", params={
            'customer': search_activity.customer_handle,
            'competitors': ",".join(minging_server_competitors_handles)
        })
        analytics = mining_response.json()
        customer_analytics = analytics.get("customer_analytics", {})
        competitors_analytics = analytics.get("competitors_analytics", [])
    except:
        analytics = {}
        customer_analytics = {}
        competitors_analytics = []
    
    customer_insights = model_to_dict(customer_insights)
    customer_insights["posting_growth"] = float(customer_insights["posting_growth"])
    customer_insights["followers_growth"] = float(customer_insights["followers_growth"])
    customer_insights["following_growth"] = float(customer_insights["following_growth"])
    
    customer_insights["often_posting_month"] = customer_analytics.get("often_posting_month", "")
    customer_insights["often_posting_week"] = customer_analytics.get("often_posting_week", "")
    customer_insights["most_liked_post"] = customer_analytics.get("most_liked_post", {})
    customer_insights["most_commented_post"] = customer_analytics.get("most_commented_post", {})
    customer_insights["best_engagement_post"] = customer_analytics.get("best_engagement_post", {})
    customer_insights["followers_gained_per_month"] = customer_analytics.get("followers_gained_per_month", [])
    customer_insights["posting_habits"] = customer_analytics.get("posting_habits", [])
    # ===================================================================================


    # BEST MONTHLY ENGAGEMENT DATA FOR CUSTOMER...
    best_monthly_engagement_data.append({
        f'{search_activity.customer_handle}_engagements': customer_analytics.get("best_monthly_engagement", [])
    })

    # BEST WEEKLY ENGAGEMENT DATA FOR CUSTOMER...
    best_weekly_engagement_data.append({
        f'{search_activity.customer_handle}_engagements': customer_analytics.get("best_weekly_engagement", [])
    })

    # MONTHLY INTERATIONS DATA OF CUSTOMER...
    monthly_interactions_data.append({
        f'{search_activity.customer_handle}_interactions': customer_analytics.get("monthly_interactions", [])
    })

    # WEEKLY INTERATIONS DATA OF CUSTOMER...
    weekly_interactions_data.append({
        f'{search_activity.customer_handle}_interactions': customer_analytics.get("weekly_interactions", [])
    })

    # COMPETITORS INSTA ANALYTICS FROM MINING SERVER...
    for analytics in competitors_analytics:
        competitor_data = competitors_data_list[competitors_analytics.index(analytics)]
        competitor_data["insights_data"]["often_posting_month"] = analytics.get("often_posting_month", "")
        competitor_data["insights_data"]["often_posting_week"] = analytics.get("often_posting_week", "")

        # BEST MONTHLY ENGAGEMENT DATA FOR COMPETITORS PROFILES...
        best_monthly_engagement_data.append({
            f'{competitor_data["profile_data"]["tiktok_userhandle"]}_engagements': analytics.get("best_monthly_engagement", [])
        })

        # BEST WEEKLY ENGAGEMENT DATA FOR COMPETITORS PROFILES...
        best_weekly_engagement_data.append({
            f'{competitor_data["profile_data"]["tiktok_userhandle"]}_engagements': analytics.get("best_weekly_engagement", [])
        })

        # MONTHLY INTERATIONS DATA OF COMPETITORS PROFILES...
        monthly_interactions_data.append({
            f'{competitor_data["profile_data"]["tiktok_userhandle"]}_interactions': analytics.get("monthly_interactions", [])
        })

        # WEEKLY INTERATIONS DATA OF COMPETITORS PROFILES...
        weekly_interactions_data.append({
            f'{competitor_data["profile_data"]["tiktok_userhandle"]}_interactions': analytics.get("weekly_interactions", [])
        })

    # ====================================================================================

    # RADIAL CHART DATA FOR CUSTOMER PROFILE...
    customer_profile["radial_chart"] = {
        'labels': ['Followers', 'Engagement', 'Posting freq'],
        'data': [int(normalize_formats_to_numbers(customer_profile['followers'])), float(customer_insights['posts_engagement']), float(customer_insights["often_posting_month"][:2])]
    }
    # =====================================================================================

    # FOLLOWERS SUMMARY TABLE FOR JOINT CUSTOMER & COMPETITORS
    followers_table = [{
        'user_handle': customer_profile["tiktok_userhandle"],
        'img_url': customer_profile["profilePicture"],
        'following_growth': customer_insights['followers_growth'],
        'post_engagement': customer_insights['posts_engagement'],
        'posting_growth': customer_insights['posting_growth'],
        'total_hashtag_posts': customer_total_hashtags_posts,
    }]

    for data in competitors_data_list:
        competitor_profile = data.get("profile_data", {})
        competitor_insights = data.get("insights_data", {})

        followers_table.append({
            'user_handle': competitor_profile["tiktok_userhandle"],
            'img_url': competitor_profile["profilePicture"],
            'following_growth': competitor_insights['followers_growth'],
            'post_engagement': competitor_insights['posts_engagement'],
            'posting_growth': competitor_insights['posting_growth'],
            'total_hashtag_posts': data.get("total_hashtag_posts", 0),
        })
    # ========================================================================================

    return Response({
        "dataset": {
            "customer_dataset": {
                'profile_data': customer_profile,
                'insights_data': customer_insights,
                'top_hashtags': customer_top_hashtags,
                'total_hashtag_posts': customer_total_hashtags_posts,
                "wordcloud_data": customer_wordcloud_data
            },
            "competitors_dataset": competitors_data_list,
            "followers_table": followers_table,
            "followers_chart_data": [],
            "best_monthly_engagement_data": get_best_monthly_engagement_data(best_monthly_engagement_data),
            "best_weekly_engagement_data": get_weekly_distribution_of_data(best_weekly_engagement_data, "engagement"),
            "monthly_interactions_data": get_monthly_interations_data(monthly_interactions_data),
            "weekly_interactions_data": get_weekly_distribution_of_data(weekly_interactions_data, "interactions"),
        }
    })
