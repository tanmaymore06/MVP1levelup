from rest_framework import serializers
from quests.models import ConceptNode


class ConceptNodeBriefSerializer(serializers.ModelSerializer):
    """
    Minimal ConceptNode representation for use inside
    Session and Dashboard responses.
    """
    class Meta:
        model = ConceptNode
        fields = ["id", "title", "order"]


class SessionSerializer(serializers.Serializer):
    '''Serializer for the Session API response, which includes the current focus node and its reinforcement nodes.
    '''
    focus_node = ConceptNodeBriefSerializer(allow_null=True)
    reinforcement_nodes = ConceptNodeBriefSerializer(many=True)


class PageCompletionSerializer(serializers.Serializer):
    '''Serializer for the response of completing a page, which indicates whether the page was completed, if the node is now completed, and the ID of the concept node.'''
    status = serializers.CharField()
    node_completed = serializers.BooleanField()
    concept_node_id = serializers.IntegerField()


class QuestProgressSerializer(serializers.Serializer):
    '''Serializer for representing the progress of a quest, including how many nodes have been completed and the total number of nodes in the quest.'''
    completed = serializers.IntegerField()
    total = serializers.IntegerField()


class DashboardSerializer(serializers.Serializer):
    '''Serializer for the Dashboard API response, which includes the user's current streak, freeze streak, total nodes completed, total sessions completed, and current quest progress.'''
    streak = serializers.IntegerField()
    freeze_streak = serializers.IntegerField()
    total_nodes_completed = serializers.IntegerField()
    total_sessions_completed = serializers.IntegerField()
    current_quest_title = serializers.CharField(allow_null=True)
    current_quest_progress = QuestProgressSerializer(allow_null=True)