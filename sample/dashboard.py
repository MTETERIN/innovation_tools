from django.db.models import Count, Sum
from django.db.models.functions import TruncMonth, TruncDay
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.template.loader import render_to_string
from innovation.models import ToolsAndInnovations, Metadata, Tweets
import dashboard
from functools import partial
from django.http import Http404
User = get_user_model()
import re
import collections
import operator
import string
from nltk.corpus import stopwords

def users_count(request):
    return render_to_string('dashboard/counter.html', {
        'title': 'Tools And Innovations Resources',
        'count': ToolsAndInnovations.objects.count(),
        'icon': '<i class="material-icons">account_circle</i>'
    })


def groups_count(request):
    return render_to_string('dashboard/counter.html', {
        'title': 'Users',
        'count': User.objects.count(),
        'icon': '<i class="material-icons">perm_identity</i>'
    })


def staff_count(request):
    User = get_user_model()

    return render_to_string('dashboard/counter.html', {
        'title': 'Staff',
        'count': User.objects.filter(is_staff=True).count(),
        'icon': '<i class="material-icons">supervisor_account</i>'
    })


def registration_stats(request):
    stats = ToolsAndInnovations.objects.values('prime_phase_number').annotate(dcount=Count('prime_phase_number'))
    stats = [stage for stage in stats if stage['prime_phase_number'].isdigit()]
    stats = sorted(stats, key=lambda tup: int(tup['prime_phase_number']))
    # stats = (
    #     User.objects
    #     .annotate(label=TruncMonth('date_joined'))
    #     .values('label')
    #     .annotate(count=Count('id'))
    # )
    return render_to_string('dashboard/stats.html', {
        'title': 'Prime Phase Number statistics',
        'stats': [
            {'label': int(stage['prime_phase_number']),
             'count': stage['dcount']}
            for stage in stats if stage['prime_phase_number'].isdigit()
        ]
    })


def login_stats(request):
    stats = ToolsAndInnovations.objects.values('prime_phase_number').annotate(dcount=Count('prime_phase_number'))
    statsWithPhase = [stage for stage in stats if stage['prime_phase_number'].isdigit()]
    stats = [stage for stage in stats if not stage['prime_phase_number'].isdigit()]
    statswithphase = sorted(statsWithPhase, key=lambda tup: int(tup['prime_phase_number']))
    statsDict = {}
    for st in statswithphase:
        try:
            metadata = Metadata.objects.get(research_phase_number=st['prime_phase_number'])
            statsDict[metadata.research_phases7] =statsDict.get(metadata.research_phases7, 0)  + st['dcount']
        except Metadata.DoesNotExist:
            statsDict['NoInformation'] =statsDict.get('NoInformation', 0)  + st['dcount']
    for st in stats:
        statsDict['NoInformation'] = statsDict.get('NoInformation', 0) + st['dcount']
    # for st in statswithphase:
    return render_to_string('dashboard/stats.html', {
        'title': 'Research Phase Stages statistics',
        'stats': [
            {'label': phase,
             'count': count}
            for phase, count in statsDict.items()
        ]
    })

def get_phasenumbers_tweets(phase_number, aggregate_function):
    tools = ToolsAndInnovations.objects.filter(prime_phase_number=phase_number).values()
    twitter_accounts = [tool['twitter'].split('/')[-1] for tool in tools if tool['twitter'].startswith('https')]
    tweets = []
    for account in twitter_accounts:
        tw = Tweets.objects.filter(topic__contains=account).values('topic').annotate(count=aggregate_function)
        for t in tw:
            tweets.append({'topic': t['topic'], 'count': t['count']})
    return tweets

def most_tweets_service(request):
    phase_number, phase = get_params(request)
    tweets = []
    title = 'Tweet statistics'
    aggregate_function = Count('topic')
    if phase_number is not None:
        stage = Metadata.objects.get(research_phase_number=phase_number)
        title = f'Tweets statistics for {stage.research_phases30}'
        tweets = get_phasenumbers_tweets(phase_number, aggregate_function)
    elif phase is not None:
        phases = Metadata.objects.filter(research_phases7=phase).values()
        if phases:
            title = f"Tweets statistics for {phases[0]['research_phases7']} stage"
            research_numbers = [phase['research_phase_number'] for phase in phases]
            for research_number in research_numbers:
                tweets.extend(get_phasenumbers_tweets(research_number, aggregate_function))
    else:
        tweets = Tweets.objects.values('topic').annotate(count=Count('topic'))


    tweets = sorted(tweets, key=lambda tup: int(tup['count']))
    tweets = tweets[-20:]
    return render_to_string('dashboard/stats.html', {
        'title': title,
        'stats': [
            {'label': tweet['topic'],
             'count': tweet['count']}
            for tweet in tweets
        ]
    })

def most_popular_service(request):
    phase_number, phase = get_params(request)
    aggregate_function = Sum('like_count')
    tweets = []
    title = 'Tweets Likes statistics'
    if phase_number is not None:
        tweets = get_phasenumbers_tweets(phase_number, aggregate_function)
        stage = Metadata.objects.get(research_phase_number=phase_number)
        if stage:
            title = f'Tweets Likes statistics for {stage.research_phases30}'
        else:
            raise Http404
    elif phase is not None:
        phases = Metadata.objects.filter(research_phases7=phase).values()
        if phases:
            title = f"Tweets Likes statistics for {phases[0]['research_phases7']} stage"
            research_numbers = [phase['research_phase_number'] for phase in phases]
            tweets = []
            for research_number in research_numbers:
                tweets.extend(get_phasenumbers_tweets(research_number, aggregate_function))
        else:
            raise Http404
    else:
        tweets = Tweets.objects.values('topic').annotate(count=aggregate_function)
    tweets = sorted(tweets, key=lambda tup: int(tup['count']))
    tweets = tweets[-20:]
    return render_to_string('dashboard/stats.html', {
        'title': title,
        'stats': [
            {'label': tweet['topic'],
             'count': tweet['count']}
            for tweet in tweets
        ]
    })

def get_params(request):
    request = request.dicts[1]['request']
    phase_number = request.GET.get('phasenumber')
    phase = request.GET.get('phase')
    return phase_number, phase

def most_retweet_service(request):
    phase_number, phase = get_params(request)
    aggregate_function = Sum('retweet')
    title = f'Tweets Retweet statistics'
    if phase_number is not None:
        tweets = get_phasenumbers_tweets(phase_number, aggregate_function)
        stage = Metadata.objects.get(research_phase_number=phase_number)
        if stage:
            title = f'Tweets Retweet statistics for {stage.research_phases30}'
        else:
            raise Http404
    elif phase is not None:
        phases = Metadata.objects.filter(research_phases7=phase).values()
        if phases:
            title = f"Tweets Retweet statistics for {phases[0]['research_phases7']} stage"
            research_numbers = [phase['research_phase_number'] for phase in phases]
            tweets = []
            for research_number in research_numbers:
                tweets.extend(get_phasenumbers_tweets(research_number, aggregate_function))
        else:
            raise Http404
    else:
        tweets = Tweets.objects.values('topic').annotate(count=aggregate_function)
    tweets = sorted(tweets, key=lambda tup: int(tup['count']))
    tweets = tweets[-20:]

    return render_to_string('dashboard/stats.html', {
        'title': title,
        'stats': [
            {'label': tweet['topic'],
             'count': tweet['count']}
            for tweet in tweets
        ]
    })

def clean_text(text):
    # remove numbers
    text_nonum = re.sub(r'\d+', '', text)
    # remove punctuations and convert characters to lower case
    text_nopunct = "".join([char.lower() for char in text_nonum if char not in string.punctuation])
    # substitute multiple whitespace with single whitespace
    # Also, removes leading and trailing whitespaces
    text_no_doublespace = re.sub('\s+', ' ', text_nopunct).strip()
    return text_no_doublespace

def word_cloud(request):
    phase_number, phase = get_params(request)
    if phase_number is not None:
        tools = ToolsAndInnovations.objects.filter(prime_phase_number=phase_number).values()
        twitter_accounts = [tool['twitter'].split('/')[-1] for tool in tools if tool['twitter'].startswith('https')]
        tweets = []
        for account in twitter_accounts:
            tw = Tweets.objects.filter(topic__contains=account).values('tweet')
            for t in tw:
                tweets.append({'tweet': t['tweet']})
    elif phase is not None:
        phases = Metadata.objects.filter(research_phases7=phase).values()
        if phases:
            research_numbers = [phase['research_phase_number'] for phase in phases]
            tweets = []
            for research_number in research_numbers:
                tools = ToolsAndInnovations.objects.filter(prime_phase_number=research_number).values()
                twitter_accounts = [tool['twitter'].split('/')[-1] for tool in tools if
                                    tool['twitter'].startswith('https')]
                tweets_low = []
                for account in twitter_accounts:
                    tw = Tweets.objects.filter(topic__contains=account).values('tweet')
                    for t in tw:
                        tweets_low.append({'tweet': t['tweet']})
                tweets.extend(tweets_low)
    else:
        tweets = Tweets.objects.all().values("tweet")
    all_tokens = [token for tweet in tweets for token in clean_text(tweet['tweet']).split()]
    counter = collections.Counter(all_tokens)
    all_tokens = {token: value for token, value in counter.items() if len(token) > 2 and token not in stopwords.words('english')}
    all_tokens = sorted(all_tokens.items(), key=operator.itemgetter(1), reverse=True)
    all_tokens = all_tokens[:150]
    return render_to_string('dashboard/stats2.html',
    {
        'stats': [
            {'word': word[0],
             'count': word[1]}
            for word in all_tokens
        ]
    }
                            )
def get_positive_tweets(phase_number, aggregate_function):
    tools = ToolsAndInnovations.objects.filter(prime_phase_number=phase_number).values()
    twitter_accounts = [tool['twitter'].split('/')[-1] for tool in tools if tool['twitter'].startswith('https')]
    tweets = []
    for account in twitter_accounts:
        tw = Tweets.objects.filter(topic__contains=account, sentiment_bert='POSITIVE').values('topic').annotate(count=aggregate_function)
        for t in tw:
            tweets.append({'topic': t['topic'], 'count': t['count']})
    return tweets

def most_positive_service(request):
    phase_number, phase = get_params(request)
    aggregate_function = Count('sentiment')
    title = f'Tweets Positive Percent statistics'
    if phase_number is not None:
        tweets = get_phasenumbers_tweets(phase_number, aggregate_function)
        positive_tweets = get_positive_tweets(phase_number, aggregate_function)
        stage = Metadata.objects.get(research_phase_number=phase_number)
        if stage:
            title = f'Tweets Positive Percent statistics for {stage.research_phases30}'
        else:
            raise Http404
    elif phase is not None:
        phases = Metadata.objects.filter(research_phases7=phase).values()
        if phases:
            title = f"Tweets Positive Percent statistics for {phases[0]['research_phases7']} stage"
            research_numbers = [phase['research_phase_number'] for phase in phases]
            tweets = []
            positive_tweets = []
            for research_number in research_numbers:
                tweets.extend(get_phasenumbers_tweets(research_number, aggregate_function))
                positive_tweets.extend(get_positive_tweets(phase_number, aggregate_function))
        else:
            raise Http404
    else:
        tweets = Tweets.objects.values('topic').annotate(count=aggregate_function)
        positive_tweets = Tweets.objects.filter(sentiment_bert='POSITIVE').values('topic').annotate(count=aggregate_function)
    stats = {}
    for tweet in tweets:
        if tweet['count'] > 100:
            stats[tweet['topic']] = {'total':tweet['count']}
    for tweet in positive_tweets:
        if stats.get(tweet['topic']) is not None:
            stats[tweet['topic']]['positive'] = tweet['count']
    for stat in stats:
        if stats[stat].get('positive') is None:
            stats[stat]['positive'] = 0
        stats[stat]['percent'] = round(stats[stat]['positive']/stats[stat]['total'],2)
    tweet_statistics = {(key, stats[key]['percent']) for key in stats}
    tweet_statistics = sorted(tweet_statistics, key=lambda tup: float(tup[1]))
    return render_to_string('dashboard/stats.html', {
        'title': title,
        'stats': [
            {'label': tweet[0],
             'count': tweet[1]*100}
            for tweet in tweet_statistics
        ]
    })

def twitters_count(request):
    return render_to_string('dashboard/counter.html', {
        'title': 'Tweets Counts',
        'count': Tweets.objects.count(),
        'icon': '<i class="material-icons">message</i>'
    })



def twitters_username_count(request):
    username_counts = len(Tweets.objects.values('username').annotate(dcount=Count('username')))
    return render_to_string('dashboard/counter.html', {
        'title': 'Twitter Username Counts',
        'count': username_counts,
        'icon': '<i class="material-icons">account_circle</i>'
    })

def twitters_topic_count(request):
    topic_counts = len(Tweets.objects.values('topic').annotate(dcount=Count('topic')))
    return render_to_string('dashboard/counter.html', {
        'title': 'Topic Counts',
        'count': topic_counts,
        'icon': '<i class="material-icons">assessment</i>'
    })

dashboard.register('Welcome', [
    [users_count, groups_count, staff_count],
    [registration_stats, login_stats]
])


dashboard.register('Tweets', [
    [twitters_count, twitters_username_count, twitters_topic_count],
    [most_tweets_service, most_popular_service],
    [most_retweet_service, most_positive_service, ], [word_cloud]]
)
