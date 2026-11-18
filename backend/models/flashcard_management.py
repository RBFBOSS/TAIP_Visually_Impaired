import uuid
from datetime import datetime
from pyecore.resources import ResourceSet, URI

def run_flashcard_component():
    rset = ResourceSet()

    print("[EMF] Loading metamodel 'flashcard_management.ecore'...")
    resource = rset.get_resource(URI('flashcard_management.ecore'))
    flashcard_pkg = resource.contents[0]

    Deck = flashcard_pkg.getEClassifier('Deck')
    Flashcard = flashcard_pkg.getEClassifier('Flashcard')
    Citation = flashcard_pkg.getEClassifier('Citation')
    ApprovalStatus = flashcard_pkg.getEClassifier('ApprovalStatus')

    citation_instance = Citation(
        id=str(uuid.uuid4()),
        sectionId=str(uuid.uuid4()),
        pageNumber=3,
        sourceExcerpt="The human visual cortex processes sensory inputs..."
    )

    flashcard_instance = Flashcard(
        id=str(uuid.uuid4()),
        question="What is the primary function of the visual cortex?",
        answer="It is responsible for processing sensory visual information.",
        createdAt=datetime.now(),
        updatedAt=datetime.now(),
        status=ApprovalStatus.DRAFT
    )
    
    flashcard_instance.citations.append(citation_instance)

    deck_instance = Deck(
        id=str(uuid.uuid4()),
        documentId=str(uuid.uuid4()),
        title="Neurology - Visual Systems Deck",
        createdAt=datetime.now()
    )
    
    deck_instance.cards.append(flashcard_instance)

    output_xmi = 'sample_deck_instance.xmi'
    xmi_resource = rset.create_resource(URI(output_xmi))
    xmi_resource.append(deck_instance)
    xmi_resource.save()

    print(f"[EMF] Succes! Modelul instantiat a fost salvat ca XMI în: {output_xmi}")

if __name__ == '__main__':
    run_flashcard_component()