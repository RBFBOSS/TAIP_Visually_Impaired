"""Definition of meta model 'flashcard'."""
from functools import partial
import pyecore.ecore as Ecore
from pyecore.ecore import *


name = 'flashcard'
nsURI = 'http://educational.app/flashcard'
nsPrefix = 'flashcard'

eClass = EPackage(name=name, nsURI=nsURI, nsPrefix=nsPrefix)

eClassifiers = {}
getEClassifier = partial(Ecore.getEClassifier, searchspace=eClassifiers)
ApprovalStatus = EEnum('ApprovalStatus', literals=['DRAFT', 'APPROVED', 'REJECTED'])


class Deck(EObject, metaclass=MetaEClass):

    id = EAttribute(eType=EString, unique=True, derived=False, changeable=True)
    documentId = EAttribute(eType=EString, unique=True, derived=False, changeable=True)
    title = EAttribute(eType=EString, unique=True, derived=False, changeable=True)
    createdAt = EAttribute(eType=EDate, unique=True, derived=False, changeable=True)
    cards = EReference(ordered=True, unique=True, containment=True, derived=False, upper=-1)

    def __init__(self, *, id=None, documentId=None, title=None, createdAt=None, cards=None):
        # if kwargs:
        #    raise AttributeError('unexpected arguments: {}'.format(kwargs))

        super().__init__()

        if id is not None:
            self.id = id

        if documentId is not None:
            self.documentId = documentId

        if title is not None:
            self.title = title

        if createdAt is not None:
            self.createdAt = createdAt

        if cards:
            self.cards.extend(cards)


class Flashcard(EObject, metaclass=MetaEClass):

    id = EAttribute(eType=EString, unique=True, derived=False, changeable=True)
    question = EAttribute(eType=EString, unique=True, derived=False, changeable=True)
    answer = EAttribute(eType=EString, unique=True, derived=False, changeable=True)
    createdAt = EAttribute(eType=EDate, unique=True, derived=False, changeable=True)
    updatedAt = EAttribute(eType=EDate, unique=True, derived=False, changeable=True)
    status = EAttribute(eType=ApprovalStatus, unique=True, derived=False, changeable=True)
    citations = EReference(ordered=True, unique=True, containment=True, derived=False, upper=-1)

    def __init__(self, *, id=None, question=None, answer=None, createdAt=None, updatedAt=None, status=None, citations=None):
        # if kwargs:
        #    raise AttributeError('unexpected arguments: {}'.format(kwargs))

        super().__init__()

        if id is not None:
            self.id = id

        if question is not None:
            self.question = question

        if answer is not None:
            self.answer = answer

        if createdAt is not None:
            self.createdAt = createdAt

        if updatedAt is not None:
            self.updatedAt = updatedAt

        if status is not None:
            self.status = status

        if citations:
            self.citations.extend(citations)


class Citation(EObject, metaclass=MetaEClass):

    id = EAttribute(eType=EString, unique=True, derived=False, changeable=True)
    sectionId = EAttribute(eType=EString, unique=True, derived=False, changeable=True)
    pageNumber = EAttribute(eType=EInt, unique=True, derived=False, changeable=True)
    sourceExcerpt = EAttribute(eType=EString, unique=True, derived=False, changeable=True)

    def __init__(self, *, id=None, sectionId=None, pageNumber=None, sourceExcerpt=None):
        # if kwargs:
        #    raise AttributeError('unexpected arguments: {}'.format(kwargs))

        super().__init__()

        if id is not None:
            self.id = id

        if sectionId is not None:
            self.sectionId = sectionId

        if pageNumber is not None:
            self.pageNumber = pageNumber

        if sourceExcerpt is not None:
            self.sourceExcerpt = sourceExcerpt
