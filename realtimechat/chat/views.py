from django.shortcuts import render, redirect
from django.contrib.auth import login
from .forms import SignupForm
import logging

logger = logging.getLogger(__name__)

def signup(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            logger.info(f'New signup: {user.email}')
            return redirect("chat")
    else:
        form = SignupForm()

    return render(request, "signup.html", {"form": form})


def chat_view(request):
    return render(request, "chat.html")