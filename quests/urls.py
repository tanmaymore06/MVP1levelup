from django.urls import path
from .views import (
    VisibleMainQuestListView,
    ConceptNodeListView,
    ConceptNodePageListView,
)

urlpatterns = [
    path("quests/", VisibleMainQuestListView.as_view(), name="quest-list"),
    path("quests/<int:quest_id>/nodes/", ConceptNodeListView.as_view(), name="node-list"),
    path("nodes/<int:node_id>/pages/", ConceptNodePageListView.as_view(), name="page-list"),
]