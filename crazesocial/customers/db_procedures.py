from instagram.models import (
    InstagramUserProfile,
    InstagramProfileInsights,
    InstagramProfileHashtag
)

from tiktok.models import (
    TiktokUserProfile,
    TiktokProfileInsights,
    TiktokProfileHashtag
)

from .profile_classification import classify_insta_profile
from .profile_classification import normalize_formats_to_numbers

def save_data_to_instagram_models(django_user, data, timestamp):
    
    if data:
        customer_profile_data = data.get("customer_dataset", {}).get("profile_data", {})
        customer_profile_insights = data.get("customer_dataset", {}).get("insights_data", {})
        customer_hashtags = customer_profile_insights.get("top_hashtags", [])

        profile_class_cust = classify_insta_profile(
            customer_profile_insights.get("post_engagement", 0.0),
            customer_profile_insights.get("reels_engagement", 0.0),
            customer_profile_data.get("followersCount", 0),
            "Instagram"
        )

        # STORING CUSTOMER PROFILE DATA
        customer_profile = InstagramUserProfile(
            django_user = django_user,
            insta_userhandle = customer_profile_data.get("username", ""),
            userInstaLink = customer_profile_data.get("userInstaLink", ""),
            fullName = customer_profile_data.get("fullName", ""),
            instaId = customer_profile_data.get("instaId", ""),
            profilePicture = customer_profile_data.get("profilePicture", ""),
            biography = customer_profile_data.get("biography", ""),
            followersCount = customer_profile_data.get("followersCount", ""),
            followCount = customer_profile_data.get("followCount", ""),
            isPrivate = customer_profile_data.get("isPrivate", ""),
            postsCount = customer_profile_data.get("postsCount", ""),
            totalHashtags = customer_profile_data.get("totalHashtags", ""),
            uniqueHashtags = customer_profile_data.get("uniqueHashtags", ""),
            category = customer_profile_data.get("category", ""),
            business_category = customer_profile_data.get("business_category", ""),
            is_business_account = customer_profile_data.get("is_business_account", ""),
            profile_class = profile_class_cust,
            wordcloud_string = data.get("customer_dataset", {}).get("wordcloud_data", ""),
            created = timestamp
        )
        
        # grabbing previous profile to calculate difference of stats in between 2 extractions...
        prev_customer_profile = InstagramUserProfile.objects.filter(
                django_user=django_user, 
                insta_userhandle=customer_profile_data.get("username", "")
            ).last()

        customer_profile.save()

        # CALCULATING POSTING, FOLLOWERS, FOLLOWING GROWTH
        # followers growth...
        try:
            followers_gr_cr = int(customer_profile.followersCount) - int(prev_customer_profile.followersCount)
            followers_gr_cr = (followers_gr_cr/int(customer_profile.followersCount)) * 100
            followers_gr_cr = round(followers_gr_cr, 1)
        except:
            followers_gr_cr = 0.0

        # followings growth
        try:
            follow_gr_cr = int(customer_profile.followCount) - int(prev_customer_profile.followCount)
            follow_gr_cr = (follow_gr_cr/int(customer_profile.followCount)) * 100
            follow_gr_cr = round(follow_gr_cr, 1)
        except:
            follow_gr_cr = 0.0

        # posting growth
        try:
            posts_gr_cr = int(customer_profile.postsCount) - int(prev_customer_profile.postsCount)
            posts_gr_cr = (posts_gr_cr/int(customer_profile.postsCount)) * 100
            posts_gr_cr = round(posts_gr_cr, 1)
        except:
            posts_gr_cr = 0.0

        InstagramProfileInsights.objects.create(
            django_user = django_user,
            insta_userhandle = customer_profile_data.get("username", ""),
            posts_engagement = customer_profile_insights.get("post_engagement", "0.0"),
            paid_posts_engagement = customer_profile_insights.get("post_engagement", "0.0"),
            reels_engagement = customer_profile_insights.get("post_engagement", "0.0"),
            posting_growth = str(posts_gr_cr),
            followers_growth = str(followers_gr_cr),
            following_growth = str(follow_gr_cr),
            created = timestamp
        )

        for hashtag in customer_hashtags:
            InstagramProfileHashtag.objects.create(
                insta_profile = customer_profile,
                hashtag_name = hashtag.get("hashtag", ""),
                item_count = hashtag.get("posts_count", ""),
                created = timestamp
            )
        
        # COMPETITORS DATA STORING PROCEDURES...
        for competitor_dataset in data.get("competitors_dataset", []):
            competitor_profile_data = competitor_dataset.get("profile_data", {})
            competitor_profile_insights = competitor_dataset.get("insights_data", {})
            competitor_hashtags = competitor_profile_insights.get("top_hashtags", [])

            profile_class = classify_insta_profile(
                competitor_dataset.get("insights_data", {}).get("post_engagement", 0.0),
                competitor_dataset.get("insights_data", {}).get("reels_engagement", 0.0),
                competitor_dataset.get("profile_data", {}).get("followersCount", 0),
                "Instagram"
            )

            competitor_profile = InstagramUserProfile(
                django_user = django_user,
                insta_userhandle = competitor_profile_data.get("username", ""),
                userInstaLink = competitor_profile_data.get("userInstaLink", ""),
                fullName = competitor_profile_data.get("fullName", ""),
                instaId = competitor_profile_data.get("instaId", ""),
                profilePicture = competitor_profile_data.get("profilePicture", ""),
                biography = competitor_profile_data.get("biography", ""),
                followersCount = competitor_profile_data.get("followersCount", ""),
                followCount = competitor_profile_data.get("followCount", ""),
                isPrivate = competitor_profile_data.get("isPrivate", ""),
                postsCount = competitor_profile_data.get("postsCount", ""),
                totalHashtags = competitor_profile_data.get("totalHashtags", ""),
                uniqueHashtags = competitor_profile_data.get("uniqueHashtags", ""),
                category = competitor_profile_data.get("category", ""),
                business_category = competitor_profile_data.get("business_category", ""),
                is_business_account = competitor_profile_data.get("is_business_account", ""),
                profile_class = profile_class,
                wordcloud_string = competitor_dataset.get("wordcloud_data", ""),
                created = timestamp
            )

            # grabbing previous profile to calculate difference of stats in between 2 extractions...
            prev_competitor_profile = InstagramUserProfile.objects.filter(
                    django_user=django_user, 
                    insta_userhandle=competitor_profile_data.get("username", "")
                ).last()
            competitor_profile.save()

            # CALCULATING POSTING, FOLLOWERS, FOLLOWING GROWTH
            # followers growth...
            try:
                followers_gr = int(competitor_profile.followersCount) - int(prev_competitor_profile.followersCount)
                followers_gr = (followers_gr/int(competitor_profile.followersCount)) * 100
                followers_gr = round(followers_gr, 1)
            except:
                followers_gr = 0.0

            # followings growth
            try:
                follow_gr = int(competitor_profile.followCount) - int(prev_competitor_profile.followCount)
                follow_gr = (follow_gr/int(competitor_profile.followCount)) * 100
                follow_gr = round(follow_gr, 1)
            except:
                follow_gr = 0.0

            # posting growth
            try:
                posts_gr = int(competitor_profile.postsCount) - int(prev_competitor_profile.postsCount)
                posts_gr = (posts_gr/int(competitor_profile.postsCount)) * 100
                posts_gr = round(posts_gr, 1)
            except:
                posts_gr = 0.0

            InstagramProfileInsights.objects.create(
                django_user = django_user,
                insta_userhandle = competitor_profile_data.get("username", ""),
                posts_engagement = competitor_profile_insights.get("post_engagement", "0.0"),
                paid_posts_engagement = competitor_profile_insights.get("post_engagement", "0.0"),
                reels_engagement = competitor_profile_insights.get("post_engagement", "0.0"),
                posting_growth = str(posts_gr),
                followers_growth = str(followers_gr),
                following_growth = str(follow_gr),
                created = timestamp
            )

            for hashtag in competitor_hashtags:
                InstagramProfileHashtag.objects.create(
                    insta_profile = competitor_profile,
                    hashtag_name = hashtag.get("hashtag", ""),
                    item_count = hashtag.get("posts_count", ""),
                    created = timestamp
                )

    print("DATA FOR INSTAGRAM EXTRACTION STORED IN DATABASE SUCCESSFULLY...")




# ======================================================================
# FUNCTION TO STORE TIKTOK EXTRACTED DATA...
# ======================================================================



def save_data_to_tiktok_models(django_user, data, timestamp):
    
    if data:
        customer_profile_data = data.get("customer_dataset", {}).get("profile_data", {})
        customer_profile_insights = data.get("customer_dataset", {}).get("insights_data", {})
        customer_hashtags = customer_profile_insights.get("top_hashtags", [])

        profile_class_cust = classify_insta_profile(
            customer_profile_insights.get("post_engagement", 0.0),
            customer_profile_insights.get("reels_engagement", 0.0),
            customer_profile_data.get("followers", 0),
            "Tiktok"
        )

        # storing customer data
        customer_profile = TiktokUserProfile(
            django_user = django_user,
            tiktok_userhandle = customer_profile_data.get("user_handle", ""),
            userprofileLink = f'https://www.tiktok.com/@{customer_profile_data.get("user_handle", "")}',
            fullName = customer_profile_data.get("fullname", ""),
            user_id = customer_profile_data.get("user_id", ""),
            sec_uid = customer_profile_data.get("sec_uid", ""),
            profilePicture = customer_profile_data.get("profile_img", ""),
            private = False if customer_profile_data.get("private", "") == "n/a" else True,
            biography = customer_profile_data.get("bio", ""),
            followers = customer_profile_data.get("followers", ""),
            followings = customer_profile_data.get("followings", ""),
            likes = customer_profile_data.get("likes", ""),
            videos_count = customer_profile_data.get("videos_count", ""),
            is_business_account = customer_profile_data.get("is_business_account", False),
            business_category = customer_profile_data.get("business_category", ""),
            is_verified = customer_profile_data.get("is_verified", False),
            profile_class = profile_class_cust,
            wordcloud_string = data.get("customer_dataset", {}).get("wordcloud_data", ""),
            created = timestamp
        )

        # grabbing previous profile to calculate difference of stats in between 2 extractions...
        prev_customer_profile = TiktokUserProfile.objects.filter(
                django_user=django_user, 
                tiktok_userhandle=customer_profile_data.get("user_handle", "")
            ).last()

        customer_profile.save()

        # CALCULATING POSTING, FOLLOWERS, FOLLOWING GROWTH
        # followers growth...
        try:
            followers_gr_cr = int(normalize_formats_to_numbers(customer_profile.followers)) - int(normalize_formats_to_numbers(prev_customer_profile.followers))
            followers_gr_cr = (followers_gr_cr/int(normalize_formats_to_numbers(customer_profile.followers))) * 100
            followers_gr_cr = round(followers_gr_cr, 1)
        except:
            followers_gr_cr = 0.0

        # followings growth
        try:
            follow_gr_cr = int(customer_profile.followings) - int(prev_customer_profile.followings)
            follow_gr_cr = (follow_gr_cr/int(customer_profile.followings)) * 100
            follow_gr_cr = round(follow_gr_cr, 1)
        except:
            follow_gr_cr = 0.0

        # posting growth
        try:
            posts_gr_cr = int(customer_profile.videos_count) - int(prev_customer_profile.videos_count)
            posts_gr_cr = (posts_gr_cr/int(customer_profile.videos_count)) * 100
            posts_gr_cr = round(posts_gr_cr, 1)
        except:
            posts_gr_cr = 0.0

        TiktokProfileInsights.objects.create(
            django_user = django_user,
            tiktok_userhandle = customer_profile_data.get("user_handle", ""),
            posts_engagement = customer_profile_insights.get("post_engagement", "0.0"),
            paid_posts_engagement = customer_profile_insights.get("paid_posts_engagement", "0.0"),
            posting_growth = str(posts_gr_cr),
            followers_growth = str(followers_gr_cr),
            following_growth = str(follow_gr_cr),
            created = timestamp
        )

        for hashtag in customer_hashtags:
            TiktokProfileHashtag.objects.create(
                tiktok_profile = customer_profile,
                hashtag_name = hashtag.get("hashtag", ""),
                item_count = hashtag.get("posts_count", ""),
                created = timestamp
            )
        
        # COMPETITORS DATA STORING PROCEDURES...
        for competitor_dataset in data.get("competitors_dataset", []):
            competitor_profile_data = competitor_dataset.get("profile_data", {})
            competitor_profile_insights = competitor_dataset.get("insights_data", {})
            competitor_hashtags = competitor_profile_insights.get("top_hashtags", [])

            profile_class = classify_insta_profile(
                competitor_profile_insights.get("post_engagement", 0.0),
                competitor_profile_insights.get("reels_engagement", 0.0),
                competitor_profile_data.get("followers", 0),
                "Tiktok"
            )

            competitor_profile = TiktokUserProfile(
                django_user = django_user,
                tiktok_userhandle = competitor_profile_data.get("user_handle", ""),
                userprofileLink = f'https://www.tiktok.com/@{competitor_profile_data.get("user_handle", "")}',
                fullName = competitor_profile_data.get("fullname", ""),
                user_id = competitor_profile_data.get("user_id", ""),
                sec_uid = competitor_profile_data.get("sec_uid", ""),
                profilePicture = competitor_profile_data.get("profile_img", ""),
                private = False if competitor_profile_data.get("private", "") == "n/a" else True,
                biography = competitor_profile_data.get("bio", ""),
                followers = competitor_profile_data.get("followers", ""),
                followings = competitor_profile_data.get("followings", ""),
                likes = competitor_profile_data.get("likes", ""),
                videos_count = competitor_profile_data.get("videos_count", ""),
                is_business_account = competitor_profile_data.get("is_business_account", False),
                business_category = competitor_profile_data.get("business_category", ""),
                is_verified = competitor_profile_data.get("is_verified", False),
                profile_class = profile_class,
                wordcloud_string = competitor_dataset.get("wordcloud_data", ""),
                created = timestamp
            )

            # grabbing previous profile to calculate difference of stats in between 2 extractions...
            prev_competitor_profile = TiktokUserProfile.objects.filter(
                    django_user=django_user, 
                    tiktok_userhandle=competitor_profile_data.get("user_handle", "")
                ).last()

            competitor_profile.save()

            # CALCULATING POSTING, FOLLOWERS, FOLLOWING GROWTH
            # followers growth...
            try:
                followers_gr = int(normalize_formats_to_numbers(competitor_profile.followers)) - int(normalize_formats_to_numbers(prev_competitor_profile.followers))
                followers_gr = (followers_gr/int(normalize_formats_to_numbers(competitor_profile.followers))) * 100
                followers_gr = round(followers_gr, 1)
            except:
                followers_gr = 0.0

            # followings growth
            try:
                follow_gr = int(competitor_profile.followings) - int(prev_competitor_profile.followings)
                follow_gr = (follow_gr/int(competitor_profile.followings)) * 100
                follow_gr = round(follow_gr, 1)
            except:
                follow_gr = 0.0

            # posting growth
            try:
                posts_gr = int(competitor_profile.videos_count) - int(prev_competitor_profile.videos_count)
                posts_gr = (posts_gr/int(competitor_profile.videos_count)) * 100
                posts_gr = round(posts_gr, 1)
            except:
                posts_gr = 0.0

            TiktokProfileInsights.objects.create(
                django_user = django_user,
                tiktok_userhandle = competitor_profile_data.get("user_handle", ""),
                posts_engagement = competitor_profile_insights.get("post_engagement", "0.0"),
                paid_posts_engagement = competitor_profile_insights.get("paid_posts_engagement", "0.0"),
                posting_growth = str(posts_gr),
                followers_growth = str(followers_gr),
                following_growth = str(follow_gr),
                created = timestamp
            )

            for hashtag in competitor_hashtags:
                TiktokProfileHashtag.objects.create(
                    tiktok_profile = competitor_profile,
                    hashtag_name = hashtag.get("hashtag", ""),
                    item_count = hashtag.get("posts_count", ""),
                    created = timestamp
                )

    print("DATA FOR TIKTOK EXTRACTION STORED IN DATABASE SUCCESSFULLY...")

