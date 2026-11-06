
from .flashcard import getEClassifier, eClassifiers
from .flashcard import name, nsURI, nsPrefix, eClass
from .flashcard import ApprovalStatus, Deck, Flashcard, Citation


from . import flashcard

__all__ = ['ApprovalStatus', 'Deck', 'Flashcard', 'Citation']

eSubpackages = []
eSuperPackage = None
flashcard.eSubpackages = eSubpackages
flashcard.eSuperPackage = eSuperPackage

Deck.cards.eType = Flashcard
Flashcard.citations.eType = Citation

otherClassifiers = [ApprovalStatus]

for classif in otherClassifiers:
    eClassifiers[classif.name] = classif
    classif.ePackage = eClass

for classif in eClassifiers.values():
    eClass.eClassifiers.append(classif.eClass)

for subpack in eSubpackages:
    eClass.eSubpackages.append(subpack.eClass)
