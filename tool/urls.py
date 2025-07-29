from django.urls import path

from .views import SummarizeTextView, TrackProgressView

urlpatterns = [
    path('summarize-text/', SummarizeTextView.as_view(), name='summarize-text'),
    path('track-progress/', TrackProgressView.as_view(), name='track-progress'),
]
