from django.utils import timezone
from django.db import IntegrityError
from datetime import timedelta
from progress.models import *
from quests.services.progression import get_session


def complete_session(user, focus_node_id):
    """
    Records the completion of the user's current Session.
    focus_node_id: the ID of the ConceptNode the user just completed.
    """
    if focus_node_id is None:
        raise ValueError("No active session — all quests completed.")

    try:
        focus_node = ConceptNode.objects.get(id=focus_node_id)
    except ConceptNode.DoesNotExist:
        raise ValueError("Focus ConceptNode does not exist.")

    focus_completed = UserNodeProgress.objects.filter(
        user=user,
        concept_node=focus_node
    ).exists()

    if not focus_completed:
        raise ValueError("Focus ConceptNode is not completed yet.")

    try:
        session_completion = SessionCompletion.objects.create(
            user=user,
            focus_node=focus_node,
            completed_at=timezone.now(),
            calendar_date=timezone.localdate(),
        )
    except IntegrityError:
        raise ValueError("Session for this focus node already recorded.")

    reinforcement_nodes = get_session(user).get("reinforcement_nodes", [])

    if reinforcement_nodes:
        session_completion.reinforcement_nodes.add(*reinforcement_nodes)

    return session_completion




def evaluate_streak_if_needed(user):
    '''lazy evaluation of user's streak based on their session completions'''
    today = timezone.localdate()

    streak_state, created = UserStreakState.objects.get_or_create(
        user=user,
        defaults={
            "streak": 0,
            "freeze_streak": 0,
            "consecutive_zero_session_days": 0,
            "last_evaluated_date": today - timedelta(days=1),
        }
    )

    if streak_state.last_evaluated_date == today:   
        return streak_state

    current_date = streak_state.last_evaluated_date + timedelta(days=1)

    while current_date <= today:
        session_count = SessionCompletion.objects.filter(
            user=user,
            calendar_date=current_date
        ).count()

        if session_count >= 1:  
            streak_state.streak += 1
            streak_state.consecutive_zero_session_days = 0

            if session_count > 2:   # reward users who do more than 2 sessions in a day by increasing their freeze streak
                streak_state.freeze_streak = min(
                    streak_state.freeze_streak + 1, 5
                )
        else:   
            streak_state.consecutive_zero_session_days += 1
            if streak_state.consecutive_zero_session_days <= 2: # allow up to 2 days of zero sessions without breaking the streak, but consume a freeze if available
                if streak_state.freeze_streak > 0:  # consume a freeze to avoid breaking the streak
                    streak_state.freeze_streak -= 1
            else:
                streak_state.streak = 0
                streak_state.consecutive_zero_session_days = 0

        current_date += timedelta(days=1)

    streak_state.last_evaluated_date = today
    streak_state.save()

    return streak_state