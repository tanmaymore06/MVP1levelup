from django.shortcuts import render

# Create your views here.

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import NotFound 


from progress.models import SessionCompletion
from progress.serializers import (
    SessionSerializer,
    PageCompletionSerializer,
    DashboardSerializer,
)
from progress.services.page_progression import complete_page
from progress.services.session_execution import (
    complete_session,
    evaluate_streak_if_needed,
)
from quests.services.progression import (
    get_session,
    get_completed_nodes,
    get_current_main_quest,
)


class SessionView(APIView):
    '''API view to retrieve the user's current session, including the focus node and reinforcement nodes.'''

    def get(self, request):
        session = get_session(request.user)
        serializer = SessionSerializer(session)
        return Response(serializer.data)


class CompleteSessionView(APIView):
    '''API view to mark the user's current session as completed. Expects the focus node ID in the request data.'''

    def post(self, request):
        focus_node_id = request.data.get("focus_node_id")

        if not focus_node_id:
            return Response(
                {"detail": "focus_node_id is required."},
                status=400
            )

        try:
            complete_session(request.user, focus_node_id)
        except ValueError as e:
            return Response({"detail": str(e)}, status=400)

        session = get_session(request.user)
        serializer = SessionSerializer(session)
        return Response(serializer.data, status=200)


class CompletePageView(APIView):
    '''API view to mark a ConceptNodePage as completed for the user. Expects the page ID as a URL parameter.'''

    def post(self, request, page_id):
        result = complete_page(request.user, page_id)
        serializer = PageCompletionSerializer(result)
        return Response(serializer.data)


class DashboardView(APIView):
    '''API view to retrieve the user's dashboard data, including current streak, freeze streak, total nodes completed, total sessions completed, and current quest progress.'''

    def get(self, request):
        user = request.user
        streak_state = evaluate_streak_if_needed(user)
        completed_nodes = get_completed_nodes(user)
        current_quest = get_current_main_quest(user, completed_nodes)

        current_quest_title = None
        current_quest_progress = None

        if current_quest:
            total = current_quest.concept_nodes.count()
            completed_in_quest = completed_nodes.filter(
                main_quest=current_quest
            ).count()
            current_quest_title = current_quest.title
            current_quest_progress = {
                "completed": completed_in_quest,
                "total": total,
            }

        data = {
            "streak": streak_state.streak,
            "freeze_streak": streak_state.freeze_streak,
            "total_nodes_completed": completed_nodes.count(),
            "total_sessions_completed": SessionCompletion.objects.filter(
                user=user
            ).count(),
            "current_quest_title": current_quest_title,
            "current_quest_progress": current_quest_progress,
        }

        serializer = DashboardSerializer(data)
        return Response(serializer.data)