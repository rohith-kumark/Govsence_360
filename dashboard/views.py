from django.shortcuts import render, HttpResponse, redirect
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login as auth_login, logout
from django.contrib import messages
from django.urls import reverse
from . models import CustomUser
import re
from youtube_transcript_api import YouTubeTranscriptApi
from .sentiment import get_sentiment
from django.views.decorators.csrf import csrf_exempt
import joblib
import pandas as pd
import string
import json
from django.http import JsonResponse
from .models import MinistryArticle


def index(request):
    return redirect('/login/')

@login_required
def dashboard(request):
    user = request.user
    if user.is_staff:
        total_count = MinistryArticle.objects.count()
        positive = MinistryArticle.objects.filter(sentiment="positive").count()
        negative = MinistryArticle.objects.filter(sentiment="negative").count()
        neutral = MinistryArticle.objects.filter(sentiment="neutral").count()
        ministry_name = 'Admin'
    else:
        total_count = MinistryArticle.objects.filter(ministry_name=user.ministry_name).count()
        positive = MinistryArticle.objects.filter(ministry_name=user.ministry_name, sentiment="positive").count()
        negative = MinistryArticle.objects.filter(ministry_name=user.ministry_name, sentiment="negative").count()
        neutral = MinistryArticle.objects.filter(ministry_name=user.ministry_name, sentiment="neutral").count()
        ministry_name = user.ministry_name
    # ministry_name = user.ministry_name if hasattr(user, 'ministry_name') else None

    context = {
        'ministry_name': ministry_name,
        'total_count': total_count,
        'positive': positive,
        'negative': negative,
        'neutral': neutral
    }
    return render(request, 'index.html', context)



def admin_view_ministry(request):
    ministry_name = request.GET.get('ministry')
    total_count = MinistryArticle.objects.filter(ministry_name=ministry_name).count()
    positive = MinistryArticle.objects.filter(ministry_name=ministry_name, sentiment="positive").count()
    negative = MinistryArticle.objects.filter(ministry_name=ministry_name, sentiment="negative").count()
    neutral = MinistryArticle.objects.filter(ministry_name=ministry_name, sentiment="neutral").count()
    # ministry_name = user.ministry_name if hasattr(user, 'ministry_name') else None

    context = {
        'ministry_name': ministry_name,
        'total_count': total_count,
        'positive': positive,
        'negative': negative,
        'neutral': neutral
    }
    return render(request, "index.html", context)


def user_logout(request):
    # Use the logout function to log the user out
    logout(request)
    # Redirect the user to a specific URL, such as the login page
    return redirect(reverse('user_login'))


def create_account(request):
    if request.user.is_authenticated:
        return redirect('/dashboard')
    if request.method == 'POST':
        # Get form data from POST request
        username = request.POST['new_username']
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        email = request.POST['email']  # Get the email field
        password = request.POST['new_password']
        ministry_name = request.POST['ministry_name']

        # Create a new CustomUser instance
        user = CustomUser.objects.create_user(
            username=username,
            first_name=first_name,
            last_name=last_name,
            email=email,  # Set the email field
            password=password,
            ministry_name=ministry_name,
        )

        # Optionally, you can log the user in after registration
        # login(request, user)

        # Redirect to a success page or any other desired page
        return redirect('/login')

    return render(request, 'create-account.html')



@csrf_exempt
def user_login(request):
    try:
        if request.user.is_authenticated:
            return redirect('/dashboard')
        
        if request.method == 'POST':
            username = request.POST.get('username')
            password = request.POST.get('password')

            # Use your CustomUser model here
            user_obj = CustomUser.objects.filter(username=username)
            
            if not user_obj.exists():
                messages.info(request, 'Account not found')
                return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
            
            user_obj = authenticate(request, username=username, password=password)

            if user_obj:
                auth_login(request, user_obj)
                return redirect('/dashboard')
            
            messages.info(request, 'Invalid Password')
            return redirect('/login')

        # Add this return statement for GET requests
        return render(request, 'login.html')
    
    except Exception as e:
        print(e)
        # Add a return statement in case of an exception
        return render(request, 'login.html')
    

def view_profile(request):
    try:
        # Get the currently authenticated user
        current_user = request.user

        # Check if the user is authenticated
        if not current_user.is_authenticated:
            # Handle the case where the user is not authenticated (e.g., redirect to login)
            return redirect('/login')

        # Render the profile template and pass the current_user to it
        return render(request, 'profile.html', {'user_profile': current_user})

    except CustomUser.DoesNotExist:
        # Handle the case where the user profile does not exist
        return render(request, '404.html')


@csrf_exempt
def youtube(request):    
    msg = None
    if request.method == 'POST':
        youtube_link = request.POST.get('youtube_link')
        print(youtube_link)
        if youtube_link:
            match = re.search(r"v=([A-Za-z0-9_-]+)", youtube_link)
            # print("YouTube Link:", match)
            if match:
                video_id = match.group(1)
            else:
                raise print("Invalid YouTube URL")
            transcript = YouTubeTranscriptApi.get_transcript(video_id)
            transcript_text = ""
            for segment in transcript:
                transcript_text += segment["text"] + " "
            sentiment = get_sentiment(transcript_text)
            msg = "The YouTube video given is of "+ sentiment.capitalize()+ " sentiment."
            print('The sentiment is', sentiment)

    context = {
        'sentiment': msg if msg is not None else "",
    }
    print(context)
    return render(request, 'youtube.html', context)


def news(request):
    msg = None
    if request.method == 'POST':
        news = request.POST.get('news')
        Model = joblib.load('dashboard/fake_news_model.pkl')
        def wordpre(text):
            text = text.lower()
            text = re.sub(r'\[.*?\]', '', text)
            text = re.sub("\\W"," ",text)
            text = re.sub(r'https?://\S+|www\.\S+', '', text)
            text = re.sub('<.*?>+', '', text)
            text = re.sub('[%s]' % re.escape(string.punctuation), '', text)
            text = re.sub('\n', '', text)
            text = re.sub(r'\w*\d\w*', '', text)
            return text
        
        txt = wordpre(news)
        txt = pd.Series(txt)
        result = Model.predict(txt)
        if result == 0:
            msg = "The given news is FAKE."
        else:
            msg = "The given news is REAL."
   
    context = {
        'result': msg if msg is not None else "",
    }
    return render(request, 'news.html', context)



def custom_404(request, exception):
    return render(request, '404.html', status=404)


@csrf_exempt
def store_news(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)  # Parse the JSON data
            ministry_name = data.get('ministry_name')
            heading = data.get('heading')
            paragraph = data.get('paragraph')
            date = data.get('date')
            source = data.get('source')
            sentiment = get_sentiment(paragraph)

            # Create a new MinistryArticle instance and save it to the database
            ministry_article = MinistryArticle(
                ministry_name=ministry_name,
                heading=heading,
                date=date,
                source=source,
                sentiment=sentiment
            )
            ministry_article.save()

            return HttpResponse(status=201)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)
    else:
        return JsonResponse({'error': 'Only POST requests are allowed'}, status=405)


