# Ghid de Integrare EMF (Eclipse Modeling Framework) & PyEcore

Un ghid pas cu pas de documentare și onboarding pentru membrii echipei la proiectul de **Tehnici Avansate în Ingineria Programării (TAIP)**.

## 1. Contextul Proiectului și Obiectivele

Aplicația noastră este un asistent educațional dedicat persoanelor cu deficiențe de vedere. Aceasta preia documente în format PDF încărcate de utilizator, le împarte în secțiuni semantice (chunks) și generează prin intermediul AI atât rezumate optimizate pentru redare audio, cât și pachete de flashcard-uri pentru învățare activă.

Pentru cerința de **Model-Driven Software Engineering (MDSE / EMF)**, am avut de realizat:
1. Definirea unui metamodel structural formal (`.ecore` / `.genmodel`) în mediul Eclipse Modeling Tools.
2. Integrarea și utilizarea efectivă a acestui metamodel în cadrul unei componente funcționale din proiect prin generare automată de cod / instanțiere conformă standardului.

### De ce PyEcore în loc de rescriere în Java?

Întregul backend al aplicației noastre este dezvoltat în **Python (FastAPI)**. Rescrierea proiectului în Java doar pentru a bifa cerința EMF ar fi fragmentat inutil arhitectura. Din acest motiv, am ales **PyEcore** — implementarea oficială a ecosistemului EMF pentru Python:
* Citește și validează fișiere autentice `.ecore`.
* Instanțiază obiectele direct în memoria Python, respectând tipurile de date și constrângerile definite în Ecore.
* Permite generarea de cod static Python (clase native) prin `pyecoregen` (echivalentul opțiunii *Generate Model Code* din Eclipse `.genmodel`).
* Salvează și citește datele în formatul standard **XMI (XML Metadata Interchange)**, fișiere care pot fi redeschise oricând în Eclipse.

## 2. Componenta Modelată: Flashcard Management

Din arhitectura completă a sistemului, am izolat subsistemul de **Management al Flashcard-urilor**:

```
+-----------------------------------------------------------------+
|                              Deck                               |
|  - id: EString                                                  |
|  - documentId: EString                                          |
|  - title: EString                                               |
|  - createdAt: EDate                                             |
|  * cards (0..*, Containment)                                    |
+-----------------------------------------------------------------+
                                |
                                v
+-----------------------------------------------------------------+
|                            Flashcard                            |
|  - id: EString                                                  |
|  - question: EString                                            |
|  - answer: EString                                              |
|  - createdAt: EDate                                             |
|  - updatedAt: EDate                                             |
|  - status: ApprovalStatus (DRAFT, APPROVED, REJECTED)           |
|  * citations (1..*, Containment)                                |
+-----------------------------------------------------------------+
                                |
                                v
+-----------------------------------------------------------------+
|                            Citation                             |
|  - id: EString                                                  |
|  - sectionId: EString                                           |
|  - pageNumber: EInt                                             |
|  - sourceExcerpt: EString  (pasajul exact extras din PDF sursă) |
+-----------------------------------------------------------------+
```

Decizii cheie de modelare:
* **`ApprovalStatus` (`EEnum`)**: Reprezintă stadiul de revizuire al unui card generat de AI (`DRAFT = 0`, `APPROVED = 1`, `REJECTED = 2`).
* **`sourceExcerpt` (`EString`)**: Păstrează fragmentul exact de text din PDF-ul original pe baza căruia AI-ul a formulat întrebarea și răspunsul. Acest lucru permite utilizatorului sau cititorului de ecran să verifice sursa și să se asigure că datele nu sunt halucinate.
* **Containment (`EReference`)**: O relație de compoziție strictă în care un `Deck` deține fizic flashcard-urile (`containment = true`, `upperBound = -1`), iar un `Flashcard` deține una sau mai multe citări (`containment = true`, `lowerBound = 1`, `upperBound = -1`).

## 3. Pasul 1: Descărcarea și Configurarea Eclipse Modeling Tools

Dacă trebuie să deschideți arborele sau să modificați vizual metamodelul în fața cadrului didactic:

1. **Cerință preliminară**: Asigurați-vă că aveți instalat un Java JDK pe calculator (versiunea 17 sau 21 este recomandată).
2. **Descărcare**:
   * Intrați pe: [eclipse.org/downloads/packages](https://www.eclipse.org/downloads/packages/)
   * **NU** descărcați varianta generică *Eclipse IDE for Java Developers*.
   * Căutați pachetul specific **Eclipse Modeling Tools** și descărcați arhiva pentru sistemul vostru de operare (Windows, macOS sau Linux).
3. **Pornire**:
   * Dezarhivați folderul într-o locație comodă (ex: `C:\EclipseModeling` sau `~/tools/eclipse`).
   * Porniți direct executabilul `eclipse` / `eclipse.exe` (nu are nevoie de instalator).
   * La pornire, când vă cere un **Workspace**, alegeți orice director și apăsați **Launch**.
4. **Setare Temă Deschisă (Light Mode)** (recomandat pentru vizibilitate clară la prezentare):
   * Mergeți în meniul de sus: `Window` -> `Preferences` (sau `Eclipse` -> `Settings` pe Mac).
   * Navigați la `General` -> `Appearance`.
   * La câmpul **Theme**, alegeți **Light** (sau **Classic**), apoi apăsați **Apply and Close**.

## 4. Pasul 2: Crearea Metamodelului Ecore în Eclipse

Iată rezumatul modului în care a fost creat fișierul `flashcard_management.ecore`:

1. **Crearea Proiectului**:
   * `File` -> `New` -> `Other...` -> Căutați `Empty EMF Project` -> Apăsați **Next**.
   * Nume proiect: `TAIP_Models` -> Apăsați **Finish**.
2. **Crearea Fișierului Ecore**:
   * Click dreapta pe folderul `model/` din proiect -> `New` -> `Other...` -> Căutați `Ecore Model` -> Apăsați **Next**.
   * Nume fișier: `flashcard_management.ecore` -> Apăsați **Finish**.
3. **Configurarea Pachetului Rădăcină (Root Package)**:
   * Deschideți fișierul, extindeți săgețica de sus (`>`) și dați click pe pictograma de folder/pachet.
   * În panoul de jos **Properties**, completați:
     * `Name`: `flashcard`
     * `Ns Prefix`: `flashcard`
     * `Ns URI`: `http://educational.app/flashcard` *(Important: URI simplu, fără paranteze sau format markdown)*.
4. **Adăugarea Elementelor**:
   * **`ApprovalStatus`**: Click dreapta pe pachet -> `New Child` -> `EEnum`. Apoi click dreapta pe el -> `New Child` -> `EEnum Literal` pentru: `DRAFT` (0), `APPROVED` (1), `REJECTED` (2).
   * **Clasele**: Click dreapta pe pachet -> `New Child` -> `EClass` pentru `Deck`, `Flashcard`, `Citation`.
   * **Atributele**: Click dreapta pe fiecare clasă -> `New Child` -> `EAttribute` (ex: `title: EString`, `pageNumber: EInt`, `createdAt: EDate`, `status: ApprovalStatus`).
   * **Relațiile**: Click dreapta pe clasă -> `New Child` -> `EReference`:
     * `Deck.cards`: `EType = Flashcard`, `UpperBound = -1`, `Containment = true`.
     * `Flashcard.citations`: `EType = Citation`, `LowerBound = 1`, `UpperBound = -1`, `Containment = true`.
5. **Salvare**: `Ctrl + S`. Fișierul `.ecore` se copiază în repository la calea `backend/models/`.

## 5. Pasul 3: Generarea Automată a Codului Python (`pyecoregen`)

În loc să scriem clasele Python de mână, folosim principiul de bază al MDE: **Codegen pe baza metamodelului formal**.

### 5.1 Instalarea Utilitarului de Generare

În terminalul mediului virtual din backend:

```bash
pip install pyecore pyecoregen
```

### 5.2 Rularea Generatorului de Cod

Navigați în folderul `backend/models/` și rulați comanda:

```bash
pyecoregen -e flashcard_management.ecore -o generated_models
```

* `-e flashcard_management.ecore`: indică fișierul metamodel sursă.
* `-o generated_models`: directorul de destinație unde va fi generat pachetul Python.

### 5.3 Ce se generează și de ce arată așa?

În folderul creat `generated_models/flashcard/` apare fișierul `flashcard.py`. Codul generat conține:
* **`metaclass=MetaEClass` și moștenirea `EObject`**: Leagă clasele Python de nucleul EMF, permițând validarea automată a tipurilor și rezolvarea relațiilor la runtime.
* **Descriptori `EAttribute` și `EReference`**:
  ```python
  cards = EReference(ordered=True, unique=True, containment=True, derived=False, upper=-1)
  ```
  Acestea definesc constrângerile declarate în Ecore (`upper=-1` = listă fără limită, `containment=True` = compoziție fizică de noduri).
* **Colecții gestionate**: La adăugarea unui element (`self.cards.extend(...)`), PyEcore setează automat pointerul către părinte conform arborelui de containment.

> **Regulă importantă:** Acest fișier este artefact generat automat; **nu se editează manual**. Dacă metamodelul se modifică în Eclipse, se re-rulează comanda `pyecoregen`.

## 6. Pasul 4: Utilizarea Modelului în Componenta Backend

Există două moduri de a rula componenta: folosind clasele generate static (recomandat) sau încărcând dinamic fișierul `.ecore`.

### 6.1 Implementarea cu Clasele Generate (`backend/models/flashcard_management.py`)

```python
import uuid
from datetime import datetime
from pathlib import Path
from pyecore.resources import ResourceSet, URI

# Importăm direct clasele generate automat de pyecoregen
from generated_models.flashcard import Deck, Flashcard, Citation, ApprovalStatus

def run_flashcard_component():
    current_dir = Path(__file__).resolve().parent
    output_xmi_path = current_dir / 'sample_deck_instance.xmi'

    # 1. Instanțiem o Citare pe baza clasei generate
    citation_instance = Citation(
        id=str(uuid.uuid4()),
        sectionId=str(uuid.uuid4()),
        pageNumber=3,
        sourceExcerpt="The human visual cortex processes sensory inputs..."
    )

    # 2. Instanțiem un Flashcard educațional
    flashcard_instance = Flashcard(
        id=str(uuid.uuid4()),
        question="What is the primary function of the visual cortex?",
        answer="It is responsible for processing sensory visual information.",
        createdAt=datetime.now(),
        updatedAt=datetime.now(),
        status=ApprovalStatus.DRAFT,
        citations=[citation_instance]
    )

    # 3. Instanțiem Deck-ul de carduri
    deck_instance = Deck(
        id=str(uuid.uuid4()),
        documentId=str(uuid.uuid4()),
        title="Neurology - Visual Systems Deck",
        createdAt=datetime.now(),
        cards=[flashcard_instance]
    )

    # 4. Serializăm instanța în format XMI (standardul EMF de persistență)
    rset = ResourceSet()
    xmi_resource = rset.create_resource(URI(str(output_xmi_path)))
    xmi_resource.append(deck_instance)
    xmi_resource.save()

    print(f"[EMF] Succes! Modelul a fost salvat ca XMI în: {output_xmi_path.name}")

if __name__ == '__main__':
    run_flashcard_component()
```

### 6.2 Rularea Componentei

Din consolă rulați:

```bash
python backend/models/flashcard_management.py
```

Ieșirea așteptată:
```text
[EMF] Succes! Modelul a fost salvat ca XMI în: sample_deck_instance.xmi
```

## 7. Ce Reprezintă Fișierul Generat `.xmi`?

Fișierul rezultat `sample_deck_instance.xmi` reprezintă serializarea standardizată **OMG XMI**:

```xml
<?xml version='1.0' encoding='UTF-8'?>
<flashcard:Deck xmlns:xmi="http://www.omg.org/XMI"
                xmlns:flashcard="http://educational.app/flashcard"
                xmi:version="2.0"
                id="c038b301-..."
                title="Neurology - Visual Systems Deck" ...>
  <cards id="7df5fa4e-..."
         question="What is the primary function of the visual cortex?"
         answer="It is responsible for processing sensory visual information."
         status="DRAFT" ...>
    <citations id="2ea1e411-..."
               pageNumber="3"
               sourceExcerpt="The human visual cortex processes sensory inputs..." />
  </cards>
</flashcard:Deck>
```

* Datorită relațiilor de tip **containment**, XML-ul include cardurile direct în nodul `Deck`, iar citările în nodul `Flashcard`.
* Dacă trageți fișierul `sample_deck_instance.xmi` în Eclipse, acesta poate fi deschis cu arborele EMF și va afișa datele create în Python.

## 8. Ghid pentru Prezentare la Laborator / Examen

La prezentare, parcurgeți următoarea demonstrație în 4 pași simpli:

1. **Arborele Ecore în Eclipse**:
   * Deschideți Eclipse Modeling Tools.
   * Extindeți `flashcard_management.ecore`.
   * Arătați pachetul rădăcină (cu `Ns URI`), enum-ul `ApprovalStatus`, clasele (`Deck`, `Flashcard`, `Citation`) și relațiile de containment.
2. **Generarea de Cod (Codegen)**:
   * Menționați comanda `pyecoregen -e flashcard_management.ecore -o generated_models`.
   * Arătați rapid fișierul `generated_models/flashcard/flashcard.py` ca dovadă a generării automate a claselor EObject din metamodel.
3. **Execuția Componentei în Python**:
   * Deschideți `flashcard_management.py` în VS Code.
   * Rulați `python flashcard_management.py` în terminal pentru a arăta execuția și instanțierea.
4. **Validarea Persistenței XMI**:
   * Deschideți `sample_deck_instance.xmi` și arătați conformitatea structurii ierarhice XML cu relațiile din metamodelul inițial.