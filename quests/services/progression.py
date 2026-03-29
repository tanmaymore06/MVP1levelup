from quests.models import ConceptNode, MainQuest
from progress.models import UserNodeProgress
import random
from collections import defaultdict


def get_completed_nodes(user):
    """
    Returns a queryset of ConceptNodes completed by the given user.
    Foundation for all progression logic — compute once and pass through.
    """
    return ConceptNode.objects.filter(
        user_progress__user=user
    )


def get_current_main_quest(user, completed_nodes=None):
    """
    Returns the current MainQuest for the user.
    The first published MainQuest (by order) that is NOT fully completed.
    Returns None if all published MainQuests are completed or none exist.
    """
    if completed_nodes is None:
        completed_nodes = get_completed_nodes(user)

    ordered_published_quests = MainQuest.objects.filter(
        is_published=True
    ).order_by("order")

    for main_quest in ordered_published_quests:
        total_nodes = main_quest.concept_nodes.count()

        if total_nodes == 0:
            continue

        completed_in_quest = completed_nodes.filter(
            main_quest=main_quest
        ).count()

        if completed_in_quest < total_nodes:
            return main_quest

    return None


def get_pending_node(user, completed_nodes=None):
    """
    Returns the first incomplete ConceptNode (by order)
    in the user's current MainQuest.
    Returns None if no pending node exists.
    """
    if completed_nodes is None:
        completed_nodes = get_completed_nodes(user)

    current_quest = get_current_main_quest(user, completed_nodes)
    if current_quest is None:
        return None

    current_quest_nodes = current_quest.concept_nodes.order_by("order")

    for node in current_quest_nodes:
        if node not in completed_nodes:
            return node

    return None


def get_visible_main_quests(user, completed_nodes=None):
    """
    Returns an ordered QuerySet of visible MainQuests for the user.
    A MainQuest is visible if it is published AND is either
    the current MainQuest or a previously completed MainQuest.
    """
    if completed_nodes is None:
        completed_nodes = get_completed_nodes(user)

    published_quests = MainQuest.objects.filter(
        is_published=True
    ).order_by("order")

    visible_ids = []

    for mq in published_quests:
        total_nodes = mq.concept_nodes.count()
        completed_in_mq = completed_nodes.filter(
            main_quest=mq
        ).count()

        visible_ids.append(mq.id)

        if completed_in_mq < total_nodes:
            break

    return MainQuest.objects.filter(id__in=visible_ids).order_by("order")


def get_visible_nodes(user, main_quest, completed_nodes=None):
    """
    Returns an ordered QuerySet of ConceptNodes in the given MainQuest
    that are visible to the user.
    Returns empty QuerySet if the MainQuest is not visible to the user.
    """
    if completed_nodes is None:
        completed_nodes = get_completed_nodes(user)

    visible_main_quests = get_visible_main_quests(user, completed_nodes)

    if main_quest not in visible_main_quests:
        return ConceptNode.objects.none()

    return ConceptNode.objects.filter(
        main_quest=main_quest
    ).order_by("order")


def get_focus_pool(user, completed_nodes=None):
    """
    Returns the single pending ConceptNode the user should focus on.
    Returns None if no pending node exists.
    """
    if completed_nodes is None:
        completed_nodes = get_completed_nodes(user)

    return get_pending_node(user, completed_nodes)


def get_reinforcement_pool(user, completed_nodes=None):
    """
    Returns a list of exactly 4 completed ConceptNodes for reinforcement,
    sampled as 2 nodes from each of 2 different MainQuests.
    Returns an empty list if conditions are not met.
    """
    if completed_nodes is None:
        completed_nodes = get_completed_nodes(user)

    if completed_nodes.count() < 6:
        return []

    nodes_by_main_quest = defaultdict(list)
    for node in completed_nodes:
        nodes_by_main_quest[node.main_quest].append(node)

    eligible_main_quests = {
        mq: nodes
        for mq, nodes in nodes_by_main_quest.items()
        if len(nodes) >= 2
    }

    if len(eligible_main_quests) < 2:
        return []

    selected_main_quests = random.sample(
        list(eligible_main_quests.keys()), 2
    )

    reinforcement_nodes = []
    for mq in selected_main_quests:
        reinforcement_nodes.extend(
            random.sample(eligible_main_quests[mq], 2)
        )

    if len(reinforcement_nodes) != 4:
        return []

    return reinforcement_nodes


def get_session(user):
    """
    Returns the current session for the user.
    Computes completed_nodes once and passes it through all calls.

    Returns:
        {
            "focus_node": ConceptNode or None,
            "reinforcement_nodes": list of 4 ConceptNodes or []
        }
    """
    completed_nodes = get_completed_nodes(user)

    focus_node = get_focus_pool(user, completed_nodes)
    reinforcement_nodes = get_reinforcement_pool(user, completed_nodes)

    return {
        "focus_node": focus_node,
        "reinforcement_nodes": reinforcement_nodes
    }