from quests.models import ConceptNode, MainQuest
from progress.models import UserNodeProgress
import random
from collections import defaultdict


def get_completed_nodes(user):
    """
    Returns a queryset of ConceptNodes completed by the given user.
    """
    return ConceptNode.objects.filter(
        user_progress__user=user # What it does: Filter ConceptNodes where there exists a UserNodeprogress entry for the given user
    )



def get_current_main_quest(user):
    """ Returns the current main quest for the user.

        current MainQuest is defined as the first published MainQuest
        ordered by 'order' that is NOT fully completed by the user.

        Returns None if:
        - the user completed all the published MainQuests, or
        - there are no published MainQuests. 
    """
    ordered_published_quests = MainQuest.objects.filter(
        is_published = True
    ).order_by("order")

    completed_nodes = get_completed_nodes(user)

    for main_quest in ordered_published_quests:
        # for each published MainQuest, we will see total ConceptNodes which exists in it, and 
        # get the ConceptNodes completed by the user, and then filter to count completed ConceptNodes exist in the MainQuest.
        #  if the count of completed nodes inside MainQuest is less than the total ConceptNodes exist in the same MainQuest then,
        # it is 'current MainQuest'.
        total_nodes = main_quest.concept_nodes.count()

        if total_nodes == 0:
            continue

        completed_nodes_in_quest = completed_nodes.filter(
            main_quest = main_quest
        ).count()

        if completed_nodes_in_quest < total_nodes:
            return main_quest
        
    return None


def get_pending_node(user):
    """
    In the current MainQuest, the first ConceptNode(by order) which is not 
    completed by the user. 
    """
    current_quest = get_current_main_quest(user)
    if current_quest is None:
        return None 
    
    current_quest_nodes = current_quest.concept_nodes.order_by("order")

    completed_nodes = get_completed_nodes(user)

    for node in current_quest_nodes:
        if node not in completed_nodes:
            return node
    return None

def get_visible_main_quests(user):
    """
    Returns a list of published MainQuests that are visible to the user,
    ordered by progression.
    A MainQuest is considered visible to the user if and only if:
    1) It is Published, 
    AND
    2) It is either, the current MainQuest OR the previously completed MainQuest.
    """
    published_quests = MainQuest.objects.filter(
        is_published=True
    ).order_by("order")

    completed_nodes = get_completed_nodes(user)

    visible_ids = []

    for mq in published_quests:
        total_nodes = mq.concept_nodes.count()
        completed_in_mq = completed_nodes.filter(
            main_quest=mq
        ).count()

        visible_ids.append(mq.id)

        if completed_in_mq < total_nodes:
            break  # stop at current main quest

    return MainQuest.objects.filter(id__in=visible_ids).order_by("order")


def get_visible_nodes(user, main_quest):
    """ 
    Def: A ConceptNode is visible to the user if and only if 
    it's parent MainQuest is visible to that user.

    Returns a list of ConceptNodes within the given MainQuest that are visible to the user,
    ordered by 'order'.
    """
    visible_main_quests = get_visible_main_quests(user)

    if main_quest not in visible_main_quests:
        return []
    return ConceptNode.objects.filter(
        main_quest=main_quest
    ).order_by("order")


# Now its time to make functions for the "Focus pool", the "Reinforcement pool", and the "Session".

def get_focus_pool(user):
    """ 
    Return the single visible ConceptNode that the user should focus on right now.
    Def: The Focus Pool contains exactly one ConceptNode:-
        the pending ConceptNode of the user.
    Returns None if there is no pending ConceptNode.
    """
    return get_pending_node(user)


def get_reinforcement_pool(user):
    """ 
    Returns the Reinforcement Pool for the user.

    The Reinforcement Pool consists of exactly 4 completed ConceptNodes,
    sampled as 2 nodes from each of 2 different MainQuests.

    Returns an empty list if the pool cannot be constructed.
    """
    completed_nodes = get_completed_nodes(user)
    if completed_nodes.count() < 6:
        return []  # Not enough completed nodes to form the pool
    
    # Group completed nodes by their MainQuest
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
    Returns the current session for the user
    
    A session consists of:
    - The Focus Pool (a single pending ConceptNode or None)
    - The Reinforcement Pool (a list of 4 completed ConceptNodes or empty list)
    """
    focus_node = get_focus_pool(user)
    reinforcement_nodes = get_reinforcement_pool(user)

    return {
        "focus_pool": focus_node,
        "reinforcement_pool": reinforcement_nodes
    }