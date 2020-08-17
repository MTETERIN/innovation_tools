from django.db import models
from django.utils.translation import ugettext_lazy as _
# Create your models here.

class Ocean(models.Model):
    name = models.CharField(_('name'), max_length=250, primary_key=True)
    area = models.BigIntegerField(_('area'))
    slug = models.SlugField(_('slug'))
    description = models.TextField(_('description'))
    map_url = models.URLField(_('map url'))

    class Meta:
        verbose_name = _('ocean')
        verbose_name_plural = _('oceans')
        ordering = ['name']

    def __str__(self):
        return self.name if self.name is not None else 'Ocean'

class Startdata(models.Model):
    name = models.CharField(max_length=30)
    description = models.CharField(max_length=30)


class Metadata(models.Model):
    research_phase_number = models.CharField(max_length=30)
    research_phases30 = models.CharField(max_length=30)
    research_phases7 = models.CharField(max_length=30)

class Tweets(models.Model):
    tweet_dt = models.DateField()
    topic = models.CharField(max_length=35)
    username = models.CharField(max_length=45)
    name = models.CharField(max_length=45)
    tweet = models.CharField(max_length=512)
    like_count = models.IntegerField()
    reply_count = models.IntegerField()
    retweet = models.IntegerField()
    retweeted = models.BooleanField()
    sentiment = models.CharField(max_length=12, default='UNKNOWN')
    score = models.FloatField(default=0.0)
    sentiment_bert = models.CharField(max_length=12, default='UNKNOWN')
    score_bert = models.FloatField(default=0.0)

class ToolsAndInnovations(models.Model):
    name = models.CharField(max_length=30, help_text="name (blue ones were added during last update)")
    url = models.CharField(max_length=30, help_text="clickable link")
    web_launchyear = models.CharField(max_length=30, default='', help_text="year of weblaunch / introduction / founding")
    prime_phase_alpha = models.CharField(max_length=30, help_text="primary phase of workflow targeted")
    prime_phase_number = models.CharField(max_length=30, default='', help_text="phase order")
    function_free = models.TextField(max_length=1000, help_text="what is/does it? (free text)")
    ui_functionfree = models.CharField(max_length=30, help_text="user input for what is/does it?")
    function_controlled = models.CharField(max_length=30, help_text="what is/does it? (controlled)")
    geo_category = models.CharField(max_length=30, help_text="open / efficient / good")
    ui_geo_category = models.CharField(max_length=30, help_text="Does the tool make science more open, efficient or good / reproducible?")
    twitter = models.CharField(max_length=30)
    twitter_follow_latest = models.CharField(max_length=30,help_text="Twitter followers")
    active_pre = models.CharField(max_length=30, help_text="preparation / define research priorities / get funding")
    active_dis = models.CharField(max_length=30, help_text="discovery, data collection")
    active_ana = models.CharField(max_length=30, help_text="analysis")
    active_wri = models.CharField(max_length=30, help_text="authoring / writing / including annotations")
    active_pub = models.CharField(max_length=30, help_text="publication / archiving / sharing")
    active_out = models.CharField(max_length=30, help_text="outreach & visibility")
    active_ass = models.CharField(max_length=30, help_text="assessment / metrics (incl. comments, discussion)")

    def __str__(self):
        return self.name


class Recommendation(models.Model):
    creators_title = models.CharField(max_length=30)
    link = models.CharField(max_length=100)