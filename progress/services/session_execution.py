from django.utils import timezone
from datetime import timedelta
from progress.models import *
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

    # Advance user progression: complete the focus ConceptNode if not already completed
    UserNodeProgress.objects.get_or_create(
        user=user,
        concept_node=focus_node,
        completed_at=timezone.now(),
    )

    return session_completion




def evaluate_streak_if_needed(user):
    today = timezone.localdate()

    streak_state = UserStreakState.objects.get_or_create(
        user=user,
        defaults={
            "streak": 0,
            "freeze_streak": 0,
            "consecutive_zero_session_days": 0,
            "last_evaluated_date": today - timedelta(days=1),  # Start evaluation from yesterday.
        }
    )

    # If already evaluated today, do nothing
    if streak_state.last_evaluated_date == today:
        return streak_state

    # Start evaluating from the next day after last evaluation
    current_date = streak_state.last_evaluated_date + timedelta(days=1)

    while current_date <= today:

        session_count = SessionCompletion.objects.filter(
            user=user,
            calendar_date=current_date
        ).count()

        # Case A: User completed at least one session
        if session_count >= 1:
            streak_state.streak += 1
            streak_state.consecutive_zero_session_days = 0

            # Freeze increment only once per day
            if session_count > 2:
                streak_state.freeze_streak = min(
                    streak_state.freeze_streak + 1,
                    5
                )
            

        # Case B: User completed zero sessions
        else:
            streak_state.consecutive_zero_session_days += 1

            if streak_state.consecutive_zero_session_days <= 2:
                # Use freeze if available
                if streak_state.freeze_streak > 0:
                    streak_state.freeze_streak -= 1
            else:
                # Third consecutive missed day resets streak
                streak_state.streak = 0
                streak_state.consecutive_zero_session_days = 0

        current_date += timedelta(days=1)

    # Mark evaluation complete
    streak_state.last_evaluated_date = today
    streak_state.save()

    return streak_state