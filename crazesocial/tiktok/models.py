from django.db import models

class TiktokUserProfile(models.Model):
    django_user         = models.CharField(max_length=500, default="n/a")
    tiktok_userhandle   = models.CharField(max_length=500, default="n/a")
    userprofileLink     = models.URLField()
    fullName            = models.CharField(max_length=500, default="n/a")
    user_id             = models.CharField(max_length=200, default="n/a")
    sec_uid             = models.CharField(max_length=500, default="n/a")
    profilePicture      = models.CharField(max_length=2000, default="n/a")
    private             = models.BooleanField(default=False)
    biography           = models.CharField(max_length=2000, default="n/a")
    followers           = models.CharField(max_length=500, default="n/a")
    followings          = models.CharField(max_length=500, default="n/a")
    likes               = models.CharField(max_length=500, default="n/a")
    videos_count        = models.CharField(max_length=500, default="n/a")
    is_business_account = models.BooleanField(default=False)
    wordcloud_string    = models.TextField(null=True, blank=True)
    business_category   = models.CharField(max_length=500, default="n/a")
    is_verified         = models.BooleanField(default=False)
    profile_class       = models.CharField(max_length=500, default="n/a")
    created             = models.CharField(max_length=500, default="n/a")

    def __str__(self):
        return f"{self.tiktok_userhandle} extracted at {self.created} by {self.django_user}"

    class Meta:
        verbose_name_plural = 'Tiktok Profiles Data'

class TiktokProfileInsights(models.Model):
    django_user            = models.CharField(max_length=500, default="n/a")
    tiktok_userhandle      = models.CharField(max_length=500, default="n/a")
    posts_engagement       = models.CharField(max_length=100, default="n/a")
    paid_posts_engagement  = models.CharField(max_length=100, default="n/a")
    posting_growth         = models.CharField(max_length=100, default="n/a")
    followers_growth       = models.CharField(max_length=100, default="n/a")
    following_growth       = models.CharField(max_length=100, default="n/a")
    created                = models.CharField(max_length=500, default="n/a")

    def __str__(self):
        return f"Insights of {self.tiktok_userhandle} at {self.created} by {self.django_user}"

    class Meta:
        verbose_name_plural = 'Tiktok Profiles Insights'


class TiktokProfileHashtag(models.Model):
    tiktok_profile = models.ForeignKey(TiktokUserProfile, related_name='hashtags', on_delete=models.CASCADE)
    hashtag_name  = models.CharField(max_length=500, default="n/a")
    item_count    = models.CharField(max_length=500, default="n/a")
    created       = models.CharField(max_length=500, default="n/a")

    def __str__(self):
        return f"Hashtag of {self.tiktok_profile.tiktok_userhandle} at {self.created}"

    class Meta:
        verbose_name_plural = 'Tiktok Profiles Hashtags'