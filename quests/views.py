from django.shortcuts import render

# Create your views here.


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .serializers import (
    MainQuestSerializer,
    ConceptNodeSerializer,
    ConceptNodePageSerializer,
)
from .models import MainQuest, ConceptNode
from quests.services.progression import (
    get_visible_main_quests,
    get_visible_nodes,
    get_completed_nodes,
    get_pending_node,
)


class VisibleMainQuestListView(APIView):
    #permission_classes = [IsAuthenticated]   Already set globally in config/settings.py

    def get(self, request):
        user = request.user
        completed_nodes = get_completed_nodes(user)  # computed once

        visible_quests = get_visible_main_quests(user, completed_nodes)

        serializer = MainQuestSerializer(
            visible_quests,
            many=True,
            context={
                "request": request,
                "completed_nodes": completed_nodes,
            }
        )
        return Response(serializer.data)


class ConceptNodeListView(APIView):
    #permission_classes = [IsAuthenticated]       Already set globally in config/settings.py

    def get(self, request, quest_id):
        user = request.user
        completed_nodes = get_completed_nodes(user)  # computed once

        try:
            main_quest = MainQuest.objects.get(id=quest_id)
        except MainQuest.DoesNotExist:
            return Response({"detail": "MainQuest not found."}, status=404)

        visible_main_quests = get_visible_main_quests(user, completed_nodes)
        if main_quest not in visible_main_quests:
            return Response({"detail": "MainQuest not visible."}, status=403)

        visible_nodes = get_visible_nodes(user, main_quest, completed_nodes)
        pending_node = get_pending_node(user, completed_nodes)

        serializer = ConceptNodeSerializer(
            visible_nodes,
            many=True,
            context={
                "request": request,
                "completed_nodes": completed_nodes,
                "pending_node": pending_node,
            }
        )
        return Response(serializer.data)


class ConceptNodePageListView(APIView):
    #permission_classes = [IsAuthenticated]     Already set globally in config/settings.py

    def get(self, request, node_id):
        try:
            node = ConceptNode.objects.get(id=node_id)
        except ConceptNode.DoesNotExist:
            return Response({"detail": "ConceptNode not found."}, status=404)

        # TODO: add visibility check for production
        pages = node.pages.all()

        serializer = ConceptNodePageSerializer(pages, many=True)
        return Response(serializer.data)