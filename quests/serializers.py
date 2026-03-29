from rest_framework import serializers
from .models import MainQuest, ConceptNode
from content.models import ConceptNodePage

# Serializers convert model instances to JSON format and vice versa, allowing for easy data exchange between the backend and frontend.

class ConceptNodePageSerializer(serializers.ModelSerializer):
    class Meta: # This is used to specify the model and fields which the frontend will receive when requesting ConceptNodePage data. It ensures that only the specified fields are included in the API response, providing a clear and concise data structure for the frontend to work with.
        model = ConceptNodePage
        fields = ["id", "title", "content", "order"]


class ConceptNodeSerializer(serializers.ModelSerializer):
    state = serializers.SerializerMethodField() # SerializerMethodField is a special type of field that allows you to define a method to determine the value of the field. In this case, the get_state method will be called to determine the state of each ConceptNode (completed, pending, or locked) based on the user's progress. This allows the frontend to easily display the appropriate status for each ConceptNode in the user interface.

    def get_state(self, obj):
        user = self.context["request"].user # The context[] dictionary is used to pass additional information to the serializer, such as the current user making the request. This allows us to determine the state of each ConceptNode based on the user's progress.
        completed_nodes = self.context["completed_nodes"]
        pending_node = self.context["pending_node"]

        if obj in completed_nodes:
            return "completed"
        if obj == pending_node:
            return "pending"
        return "locked"

    class Meta:
        model = ConceptNode
        fields = ["id", "title", "order", "state"]


class MainQuestSerializer(serializers.ModelSerializer):
    is_completed = serializers.SerializerMethodField()

    def get_is_completed(self, obj):
        '''Determines if the MainQuest is completed by comparing the number of completed ConceptNodes to the total number of ConceptNodes in the MainQuest. 
        If all ConceptNodes are completed, it returns True; otherwise, it returns False. 
        This allows the frontend to easily display whether a MainQuest is completed or not based on the user's progress.'''
        
        completed_nodes = self.context["completed_nodes"]
        total_nodes = obj.concept_nodes.count()
        if total_nodes == 0:
            return False
        completed_in_quest = completed_nodes.filter(
            main_quest=obj
        ).count()
        return completed_in_quest == total_nodes

    class Meta:
        model = MainQuest
        fields = ["id", "title", "order", "is_completed"]