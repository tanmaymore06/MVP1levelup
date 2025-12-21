<h1>Derived State Logic (MVP-1)</h1>

<h3>1. Getting Concept Nodes Completed By The User - <I>get_completed_nodes(user)</I></h3>  

A ConceptNode is considered "completed" for a user if and only if
there exists a UserNodeProgress entry for that (user, concept_node) pair.


- <B>What This Function Must Do </B>

    Given a user, it must:

    Look at UserNodeProgress
    Find which ConceptNodes the user has completed
    Return them as a queryset of ConceptNode

    - Work correctly even if:
       - user has completed nothing, and
       - tables are empty

- This logic:
    - works with empty databases
    - returns an empty queryset for new users
    - is used as the foundation for all progression rules
