from django.db import models

# Create your models here.
class MainQuest(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    order = models.PositiveIntegerField(unique=True)
    is_published = models.BooleanField(default=False)

    class Meta: # Ensures MainQuests are ordered by 'order' field by default
        ordering = ['order']

    def __str__(self):
        return f"MQTitle: {self.title} MQDesc: {self.description}"



class ConceptNode(models.Model):
    main_quest = models.ForeignKey(
        MainQuest,
        on_delete=models.CASCADE,
        related_name='concept_nodes' # Added related_name for reverse access. For example: main_quest.concept_nodes.all()
    )
    title = models.CharField(max_length=255)
    order = models.PositiveIntegerField()

    class Meta:
        ordering = ['order']
        constraints = [ 
            models.UniqueConstraint( # Ensures unique order of ConceptNodes within each MainQuest
                fields=['main_quest', 'order'],  # Fields that must be unique together i.e., each ConceptNode's order within a MainQuest must be unique
                name='unique_node_order_per_mainquest' # Constraint name
            )
        ]

    def __str__(self):
        return f"MQTitle: {self.main_quest.title} CNTitle: {self.title} CNOrder: {self.order}" 