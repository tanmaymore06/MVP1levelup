from quests.models import ConceptNode
from progress.models import UserNodeProgress


def get_completed_nodes(user):
    """
    Returns a queryset of ConceptNodes completed by the given user.
    """
    return ConceptNode.objects.filter(
        user_progress__user=user # What it does: Filter ConceptNodes where there exists a UserNodeprogress entry for the given user
    )

