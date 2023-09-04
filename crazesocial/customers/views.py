from django.shortcuts import render
from django.http import JsonResponse
from django.core.files.storage import FileSystemStorage
from django.core.files import File
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
import datetime
import requests

from .models import *
from .tasks import social_extraction_join_task
from .utils import retrieve_and_save_data_from_backend, mark_common_competitors_handles
from .input_data_enrichment import populate_instagram_input, populate_tiktok_input
from .profile_classification import get_dashboard_monthly_engagement, get_social_evolution_data

def home_page(request):
    return render(request, 'customers.html', {})

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_view(request):

    logged_in_user = request.user.first_name

    try:
        profile_image = f"http://3.139.124.188{request.user.profile_image.url}"
    except:
        profile_image = ''

    customer = request.user.customer_profile

    tiktok_competitors = [competitor.tiktok_user_handle for competitor in customer.competitors.all()]
    insta_competitors = [competitor.insta_user_handle for competitor in customer.competitors.all()]

    tiktok_connected = all(tiktok_competitors)
    instagram_connected = all(insta_competitors)

    engagements_data = get_dashboard_monthly_engagement(customer)

    is_new_user = not tiktok_connected or not instagram_connected

    return Response({
        "is_new_user": is_new_user,
        "is_tiktok_connected": tiktok_connected,
        "is_instagram_connected": instagram_connected,
        "last_login_date": request.user.last_login.strftime("%d %B, %Y, %H:%M"),
        "account_usage": 0,
        "user_monthly_engagement": engagements_data,
        "social_evolution": get_social_evolution_data(engagements_data),
        "loggedin_user": logged_in_user,
        "user_id": request.user.id,
        "username": request.user.username,
        "profile_image": profile_image
    }, 200)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def data_extraction_view(request, flow_name):
    timestamp = str(datetime.datetime.now())
    username = request.user.username
    customer = request.user.customer_profile

    if flow_name == 'Instagram':
        customer_handle = customer.insta_user_handle
        competitor_handles = [competitor.insta_user_handle for competitor in customer.competitors.all() if '---common---' not in competitor.insta_user_handle]
        common_handles = [competitor.insta_user_handle for competitor in customer.competitors.all() if '---common---' in competitor.insta_user_handle]

    elif flow_name == 'Tiktok':
        customer_handle = customer.tiktok_user_handle
        competitor_handles = [competitor.tiktok_user_handle for competitor in customer.competitors.all() if '---common---' not in competitor.tiktok_user_handle]
        common_handles = [competitor.tiktok_user_handle for competitor in customer.competitors.all() if '---common---' in competitor.tiktok_user_handle]

    elif flow_name == 'Influencer':
        pass

    if UserActivity.objects.filter(customer=customer, django_user=username, status=False, flow_name=flow_name).exists():
        return JsonResponse({"message": f"Already running an extraction for {flow_name}"})

    # capture the activity
    UserActivity.objects.create(
        customer= customer,
        django_user= username,
        customer_handle= customer_handle,
        competitors=",".join(competitor_handles),
        common_profiles=",".join(common_handles),
        flow_name=flow_name,
        created= timestamp
    )

    social_insta_join_task = social_extraction_join_task.delay(username, customer_handle, competitor_handles, timestamp, flow_name, request)

    return Response({
        "django_user": username,
        "customer_handle": customer_handle,
        "competitor_handles": competitor_handles,
        "common_handles": common_handles,
        "flow_name": flow_name,
        "timestamp": timestamp,
        "message": "Task started successfully"
    }, 200)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def extraction_status_check_view(request, flow_name):

    try:
        activity_object = UserActivity.objects.get(django_user=request.user.username, status=False, flow_name=flow_name)

        if activity_object.flow_name == "Instagram":
            url = f"http://66.94.109.65/instagram/crazysocial/bulk_extraction/check/"
        elif activity_object.flow_name == "Tiktok":
            url = f"http://66.94.109.65/tiktok/crazysocial/joint_status_check/"

        queries = [activity_object.customer_handle] + activity_object.competitors.split(',')
        queries = "----".join(queries)

        response = requests.get(url, params={
            "username": activity_object.django_user,
            "queries": queries,
            "timestamp": activity_object.created
        })

        if response.json().get("status") == True:
            # =========================================
            # FOR DATA SAVING, ON EXTRACTION COMPLETION
            # =========================================
            
            retrieve_and_save_data_from_backend(
                request, 
                activity_object.flow_name,
                activity_object.created
            )

            activity_object.status = True
            activity_object.save()
            return Response({
                "completed": True, 
                "message": f"Extraction of {activity_object.customer_handle} is Completed...!"
            }, 200)
    except Exception as e:
        return Response({"completed": False, "message": f"Exception: {e}"}, 400)

    return Response({"completed": False, "message": "Empty..."}, 200)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def platform_connect_view(request):
    flow_name = request.POST["flow_name"]
    username = request.POST["username"]
    password = request.POST["password"]

    competitors_handles = [
        request.POST.get("competitor1", ""), 
        request.POST.get("competitor2", ""), 
        request.POST.get("competitor3", ""), 
        request.POST.get("competitor4", "")
    ]

    if flow_name == "Instagram":
        response, status = populate_instagram_input(request, username, password, competitors_handles)
        return Response(response, status=status)

    elif flow_name == "Tiktok":
        response, status = populate_tiktok_input(request, username, password, competitors_handles)
        return Response(response, status=status)

    return Response({
        'flow_name': flow_name,
        'credentials': {
            'username': username,
            'password': password
        },
        'competitors': competitors_handles
    }, status=200)

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def profile_settings_view(request):
    user_profile = request.user

    if request.method == "GET":

        try:
            profile_image = f"http://3.139.124.188{user_profile.profile_image.url}"
        except: profile_image = ""

        return Response({
            "first_name": user_profile.first_name,
            "last_name": user_profile.last_name,
            "gender": user_profile.gender,
            "bio": user_profile.bio,
            "profile_image": profile_image
        }, status=200)

    elif request.method == "POST":
        
        # PROFILE ATTIRBUTES...
        user_profile.first_name = request.POST.get("first_name", user_profile.first_name)
        user_profile.last_name = request.POST.get("last_name", user_profile.last_name)
        user_profile.bio = request.POST.get("bio", user_profile.bio)
        user_profile.gender = request.POST.get("gender", user_profile.gender)

        # PROFILE IMAGE SAVING PROCEDURE...
        try:
            myfile = request.FILES['profile_image']
            fs = FileSystemStorage()
            filename = fs.save(myfile.name, myfile)
            uploaded_file_url = fs.url(filename)

            with open(f"/home/ubuntu/CrazeSocial/crazesocial{uploaded_file_url.replace('%20', ' ')}", 'rb') as doc_file:
                user_profile.profile_image.save(
                    filename, File(doc_file), save=True
                )
                # user_profile.save()
        except:
            pass

        user_profile.save()

        return Response({
            "message": "Profile Updated successfully...",
            "status": "OK"
        }, status=200)

    return Response({"status": "FAILED"}, status=400)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def personal_settings_view(request, flow_name):

    customer_profile = request.user.customer_profile
    competitors_objects = customer_profile.competitors.all()

    if request.method == "GET":
        response = {}

        if flow_name == "Instagram":
            competitors_handles = [competitor.insta_user_handle for competitor in competitors_objects]

        elif flow_name == "Tiktok":
            competitors_handles = [competitor.tiktok_user_handle for competitor in competitors_objects]

        for myhandle in competitors_handles:
            try:
                competitors_handles[competitors_handles.index(myhandle)] = myhandle.split('---common---')[0]
            except:
                pass

        for handle in competitors_handles:
            response[f"competitor_{competitors_handles.index(handle)+1}"] = handle

        return Response({
            "competitors": response,
            "flow_name": flow_name
        }
        , status=200)

    elif request.method == "POST":
        
        competitors_data = [
            request.POST.get("competitor_1", ""),
            request.POST.get("competitor_2", ""),
            request.POST.get("competitor_3", ""),
            request.POST.get("competitor_4", ""),
        ]

        competitors_data = mark_common_competitors_handles(competitors_data, flow_name, request.user)
        
        for competitor_object, competitor_data in zip(competitors_objects, competitors_data):

            if flow_name == "Instagram":
                competitor_object.insta_user_handle = competitor_data
            elif flow_name == "Tiktok":
                competitor_object.tiktok_user_handle = competitor_data

            competitor_object.save()

        return Response({
            "message": f"{flow_name} competitors updated successfully...",
            "status": "OK"
        }, status=200)

    return Response({
        "message": "something went wrong",
        "status": "FAILED"
    }, status=400)

