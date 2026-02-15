from django.utils import timezone
from progress.models import SessionCompletion
from quests.services.progression import get_session


def complete_session(user):
    """
    Records the completion of the user's current Session.
    Persists the Focus ConceptNode and Reinforcement ConceptNodes (if any).
    """
    session = get_session(user)

    focus_node = session["focus_node"]
    reinforcement_nodes = session.get("reinforcement_nodes", [])

    session_completion = SessionCompletion.objects.create(
        user=user,
        focus_node=focus_node,
        completed_at=timezone.now(),
        calendar_date=timezone.localdate(),
    )

    if reinforcement_nodes:
        session_completion.reinforcement_nodes.add(*reinforcement_nodes)

    return session_completion
