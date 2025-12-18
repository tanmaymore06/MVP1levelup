from django.db import models

# Create your models here.
from django.contrib.auth.models import User # Using Django's built-in User model
from quests.models import ConceptNode


class UserNodeProgress(models.Model):
    user = models.ForeignKey( 
        User,
        on_delete=models.CASCADE,
        related_name='node_progress'
    )
    concept_node = models.ForeignKey( 
        ConceptNode,
        on_delete=models.CASCADE,
        related_name='user_progress'
    )
    completed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint( # Ensures a user can only complete a ConceptNode once
                fields=['user', 'concept_node'],
                name='unique_user_node_completion'
            )
        ]

    def __str__(self):
        return f"{self.user.username} completed the Concept Node {self.concept_node.title} at {self.completed_at}"
