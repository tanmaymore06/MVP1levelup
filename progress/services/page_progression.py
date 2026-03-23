from django.utils import timezone
from django.db import transaction

from content.models import ConceptNodePage
from progress.models import  UserPageProgress, UserNodeProgress


@transaction.atomic
def complete_page(user, page_id):
    """
    Marks a ConceptNodePage as completed for a user.

    Steps:
    1. Validate the page exists.
    2. Create a UserPageProgress record (if not already present).
    3. Check whether all pages of the ConceptNode are completed.
    4. If yes, create UserNodeProgress.
    """

    page = ConceptNodePage.objects.select_related("concept_node").get(id=page_id)

    # Prevent duplicate completion
    progress, created = UserPageProgress.objects.get_or_create( # The 'progress' variable is not used here, but it ensures we have a progress record to work with. In sort, it initializes the progress for new pages.
        user=user,
        page=page,
        defaults={"completed_at": timezone.now()}
    )

    if not created:
        return {
            "status": "already_completed",
            "node_completed": False,
            "concept_node_id": page.concept_node.id
        }

    concept_node = page.concept_node

    total_pages = ConceptNodePage.objects.filter(
        concept_node=concept_node
    ).count()

    completed_pages = UserPageProgress.objects.filter(
        user=user,
        page__concept_node=concept_node
    ).count()

    node_completed = False

    if completed_pages == total_pages:

        UserNodeProgress.objects.get_or_create(
            user=user,
            concept_node=concept_node,
            defaults={"completed_at": timezone.now()}
        )

        node_completed = True

    return {
        "status": "page_completed",
        "node_completed": node_completed,
        "concept_node_id": concept_node.id
    }