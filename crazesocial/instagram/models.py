from tabnanny import verbose
from django.db import models

class InstagramUserProfile(models.Model):
    django_user         = models.CharField(max_length=500, default="n/a")
    insta_userhandle    = models.CharField(max_length=500, default="n/a")
    userInstaLink       = models.URLField()
    fullName            = models.CharField(max_length=500, default="n/a")
    instaId             = models.CharField(max_length=200, default="n/a")
    profilePicture      = models.CharField(max_length=2000, default="n/a")
    biography           = models.CharField(max_length=2000, default="n/a")
    followersCount      = models.CharField(max_length=500, default="n/a")
    followCount         = models.CharField(max_length=500, default="n/a")
    isPrivate           = models.BooleanField(default=False)
    postsCount          = models.CharField(max_length=500, default="n/a")
    totalHashtags       = models.CharField(max_length=500, default="n/a")
    uniqueHashtags      = models.CharField(max_length=500, default="n/a", null=True)
    category            = models.CharField(max_length=500, default="n/a", null=True)
    business_category   = models.CharField(max_length=500, default="n/a", null=True)
    is_business_account = models.BooleanField(default=False, null=True)
    profile_class       = models.CharField(max_length=500, default="n/a")
    wordcloud_string    = models.TextField(null=True, blank=True)
    created             = models.CharField(max_length=500, default="n/a")

    def __str__(self):
        return f"{self.insta_userhandle} extracted at {self.created} by {self.django_user}"

    class Meta:
        verbose_name_plural = 'Instagram Profiles Data'

class InstagramProfileInsights(models.Model):
    django_user           = models.CharField(max_length=500, default="n/a")
    insta_userhandle      = models.CharField(max_length=500, default="n/a")
    posts_engagement      = models.CharField(max_length=100, default="n/a")
    paid_posts_engagement = models.CharField(max_length=100, default="n/a")
    reels_engagement      = models.CharField(max_length=100, default="n/a")
    posting_growth        = models.CharField(max_length=100, default="n/a")
    followers_growth      = models.CharField(max_length=100, default="n/a")
    following_growth      = models.CharField(max_length=100, default="n/a")
    created               = models.CharField(max_length=500, default="n/a")

    def __str__(self):
        return f"Insights of {self.insta_userhandle} at {self.created} by {self.django_user}"

    class Meta:
        verbose_name_plural = 'Instagram Profiles Insights'

class InstagramProfileHashtag(models.Model):
    insta_profile = models.ForeignKey(InstagramUserProfile, related_name='hashtags', on_delete=models.CASCADE)
    hashtag_name  = models.CharField(max_length=500, default="n/a")
    item_count    = models.CharField(max_length=500, default="n/a")
    created       = models.CharField(max_length=500, default="n/a")

    def __str__(self):
        return f"Hashtag of {self.insta_profile.insta_userhandle} at {self.created}"

    class Meta:
        verbose_name_plural = 'Instagram Profiles Hashtags'