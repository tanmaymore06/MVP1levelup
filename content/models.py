from django.db import models

# Create your models here.
from quests.models import ConceptNode


class ConceptNodePage(models.Model):
    '''This model represents a page of content associated with a ConceptNode. 
    Each ConceptNode can have multiple pages, and each page has an order to determine its sequence within the ConceptNode.'''

    concept_node = models.ForeignKey( 
        ConceptNode,
        on_delete=models.CASCADE,
        related_name='pages' 
    )
    title = models.CharField(max_length=255, blank=True)
    content = models.TextField() # This is where the main content of the page will be stored in the form of Markdown text. 
    order = models.PositiveIntegerField()

    class Meta:
        ordering = ['order']
        constraints = [
            models.UniqueConstraint( # Ensures unique order of ConceptNodePages within each ConceptNode
                fields=['concept_node', 'order'],
                name='unique_page_order_per_concept_node'
            )
        ]

    def __str__(self):
        return f"Title of Concept Node: {self.concept_node.title} → Title of the Page: {self.title} (Order: {self.order})"
