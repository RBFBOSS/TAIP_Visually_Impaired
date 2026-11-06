import uuid
from datetime import datetime
from pyecore.resources import ResourceSet, URI

def run_flashcard_component():
    # 1. Inițializăm containerul de resurse PyEcore
    rset = ResourceSet()

    # 2. Încărcăm metamodelul generat din Eclipse
    print("[EMF] Loading metamodel 'flashcard_management.ecore'...")
    resource = rset.get_resource(URI('flashcard_management.ecore'))
    flashcard_pkg = resource.contents[0]

    # 3. Extragem entitățile (EClasses) și Enum-ul din pachet
    Deck = flashcard_pkg.getEClassifier('Deck')
    Flashcard = flashcard_pkg.getEClassifier('Flashcard')
    Citation = flashcard_pkg.getEClassifier('Citation')
    ApprovalStatus = flashcard_pkg.getEClassifier('ApprovalStatus')

    # 4. Instanțiem o Citare (sursa extrasă din document pentru cititorul de ecran)
    citation_instance = Citation(
        id=str(uuid.uuid4()),
        sectionId=str(uuid.uuid4()),
        pageNumber=3,
        sourceExcerpt="The human visual cortex processes sensory inputs..."
    )

    # 5. Instanțiem un Flashcard educațional
    flashcard_instance = Flashcard(
        id=str(uuid.uuid4()),
        question="What is the primary function of the visual cortex?",
        answer="It is responsible for processing sensory visual information.",
        createdAt=datetime.now(),
        updatedAt=datetime.now(),
        status=ApprovalStatus.DRAFT
    )
    
    # Adăugăm citarea în lista de citări a flashcard-ului (EReference 'citations')
    flashcard_instance.citations.append(citation_instance)

    # 6. Instanțiem Deck-ul de carduri
    deck_instance = Deck(
        id=str(uuid.uuid4()),
        documentId=str(uuid.uuid4()),
        title="Neurology - Visual Systems Deck",
        createdAt=datetime.now()
    )
    
    # Adăugăm cardul în pachet (EReference 'cards')
    deck_instance.cards.append(flashcard_instance)

    # 7. Serializăm instanța în format XMI (standardul EMF pentru persistență)
    output_xmi = 'sample_deck_instance.xmi'
    xmi_resource = rset.create_resource(URI(output_xmi))
    xmi_resource.append(deck_instance)
    xmi_resource.save()

    print(f"[EMF] Succes! Modelul instanțiat a fost salvat ca XMI în: {output_xmi}")

if __name__ == '__main__':
    run_flashcard_component()