from django.db import models

# Create your models here.
from django.contrib.auth.models import User # Using Django's built-in User model
from quests.models import ConceptNode


class UserNodeProgress(models.Model):
    """
    This model tracks the progress of a user.
    Each time a user completes a Pending ConceptNode, a new record is created
    which stores the user, the completed ConceptNode, and 
    the date and time of completion.
    """
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



class SessionCompletion(models.Model):
    """  
    This model tracks the completion of a session by a user.
    Each time a user completes a session, a new record is created 
    which stores the user, completed Focus Node and Reinforcement Nodes (if any reinforcement nodes were completed), and
    the date, time and day of completion.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="session_completions",
    )

    focus_node = models.ForeignKey(
        ConceptNode,
        on_delete=models.PROTECT,
        related_name="focused_in_sessions",
    )

    reinforcement_nodes = models.ManyToManyField(
        ConceptNode,
        related_name="reinforced_in_sessions",
        blank=True,
    )

    completed_at = models.DateTimeField(auto_now_add=True)
    calendar_date = models.DateField()

    class Meta:
        ordering = ["-completed_at"]
        unique_together = ("user", "calendar_date", "completed_at")
    
    def __str__(self):
        return f"{self.user.username} completed a session focused on {self.focus_node.title} at {self.completed_at}"