# Ghid de Integrare EMF (Eclipse Modeling Framework) & PyEcore

Un ghid pas cu pas de documentare și onboarding pentru membrii echipei la proiectul de **Tehnici Avansate în Ingineria Programării (TAIP)**.

---

## 1. Contextul Proiectului și Obiectivele

Aplicația noastră este un asistent educațional dedicat persoanelor cu deficiențe de vedere. Aceasta preia documente în format PDF încărcate de utilizator, le împarte în secțiuni semantice (chunks) și generează prin intermediul AI atât rezumate optimizate pentru redare audio, cât și pachete de flashcard-uri pentru învățare activă.

Pentru cerința de **Model-Driven Software Engineering (MDSE / EMF)**, am avut de realizat:
1. Definirea unui metamodel structural formal (`.ecore` / `.genmodel`) în mediul Eclipse Modeling Tools.
2. Integrarea și utilizarea efectivă a acestui metamodel în cadrul unei componente funcționale din proiect.

### De ce PyEcore în loc de rescriere în Java?
Întregul backend al aplicației noastre este dezvoltat în **Python (FastAPI)**. Rescrierea proiectului în Java doar pentru a bifa cerința EMF ar fi fragmentat inutil arhitectura. Din acest motiv, am ales **PyEcore** — implementarea oficială a ecosistemului EMF pentru Python:
* Citește și validează fișiere autentice `.ecore`.
* Instanțiază obiectele direct în memoria Python, respectând tipurile de date și constrângerile definite în Ecore.
* Salvează și citește datele în formatul standard **XMI (XML Metadata Interchange)**, fișiere care pot fi redeschise oricând în Eclipse.

---

## 2. Componenta Modelată: Flashcard Management

Din arhitectura completă a sistemului, am izolat subsistemul de **Management al Flashcard-urilor**:

```text
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

---

## 3. Pasul 1: Descărcarea și Configurarea Eclipse Modeling Tools

Dacă trebuie să deschideți arborele sau să modificați vizual metamodelul în fața cadrului didactic:

1. **Cerință preliminară**: Asigurați-vă că aveți instalat un Java JDK pe calculator (versiunea 17 sau 21 este recomandată).
2. **Descărcare**:
   * Intrați pe: [https://www.eclipse.org/downloads/packages/](https://www.eclipse.org/downloads/packages/)
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

---

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
5. **Salvare**: `Ctrl + S`. Fișierul `.ecore` este salvat în repository la calea `backend/models/`.

---

## 5. Pasul 3: Integrarea și Rularea în Python

Metamodelul definit este încărcat dinamic în backend-ul nostru de Python cu ajutorul `pyecore`.

### 5.1 Configurarea Mediului

Asigurați-vă că sunteți în directorul proiectului și că mediul virtual Python este activat:

```bash
# Activare mediu virtual (Windows PowerShell)
.\backend\.venv\Scripts\Activate.ps1

# (Sau pe Linux / macOS)
# source backend/.venv/bin/activate

# Instalare dependență PyEcore
pip install pyecore
```

### 5.2 Codul Componentei Python (`backend/models/flashcard_management.py`)

Acest script încarcă schema `.ecore`, instanțiază obiectele de domeniu, le asociază și le serializează într-un fișier XMI:

```python
import uuid
from datetime import datetime
from pathlib import Path
from pyecore.resources import ResourceSet, URI

def run_flashcard_component():
    current_dir = Path(__file__).resolve().parent
    ecore_path = current_dir / 'flashcard_management.ecore'
    output_xmi_path = current_dir / 'sample_deck_instance.xmi'

    if not ecore_path.exists():
        raise FileNotFoundError(f"Nu s-a găsit metamodelul: {ecore_path}")

    # 1. Inițializăm containerul de resurse PyEcore
    rset = ResourceSet()

    # 2. Încărcăm metamodelul exportat din Eclipse
    print(f"[EMF] Se încarcă metamodelul din: {ecore_path.name}...")
    resource = rset.get_resource(URI(str(ecore_path)))
    flashcard_pkg = resource.contents[0]

    # 3. Obținem referințe către clase și enum-uri folosind metoda conformă getEClassifier
    Deck = flashcard_pkg.getEClassifier('Deck')
    Flashcard = flashcard_pkg.getEClassifier('Flashcard')
    Citation = flashcard_pkg.getEClassifier('Citation')
    ApprovalStatus = flashcard_pkg.getEClassifier('ApprovalStatus')

    # 4. Instanțiem o Citare (referința către sursa extrasă pentru cititorul de ecran)
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
    flashcard_instance.citations.append(citation_instance)

    # 6. Instanțiem Deck-ul rădăcină
    deck_instance = Deck(
        id=str(uuid.uuid4()),
        documentId=str(uuid.uuid4()),
        title="Neurology - Visual Systems Deck",
        createdAt=datetime.now()
    )
    deck_instance.cards.append(flashcard_instance)

    # 7. Serializăm instanța în format XMI
    xmi_resource = rset.create_resource(URI(str(output_xmi_path)))
    xmi_resource.append(deck_instance)
    xmi_resource.save()

    print(f"[EMF] Succes! Instanța modelului a fost serializată în: {output_xmi_path.name}")

if __name__ == '__main__':
    run_flashcard_component()
```

### 5.3 Rularea Scriptului

Din consolă, rulați:

```bash
python backend/models/flashcard_management.py
```

Ieșirea așteptată:

```text
[EMF] Se încarcă metamodelul din: flashcard_management.ecore...
[EMF] Succes! Instanța modelului a fost serializată în: sample_deck_instance.xmi
```

---

## 6. Ce Reprezintă Fișierul Generat `.xmi`?

Fișierul rezultat `sample_deck_instance.xmi` nu este un XML oarecare, ci un fișier standardizat de persistență **OMG XMI**:

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

* Datorită setării relațiilor de tip **containment**, XML-ul include cardurile direct în interiorul nodului `Deck`, iar citările în interiorul nodului `Flashcard`.
* Dacă acest fișier `.xmi` este tras înapoi în Eclipse, Eclipse EMF îl va recunoaște și îl va afișa sub formă de arbore vizual populat cu datele din Python.

---

## 7. Ghid pentru Prezentare la Laborator / Examen

La prezentare, parcurgeți următoarea demonstrație în 3 pași:

1. **Arătați Arborele Metamodelului în Eclipse**:
   * Deschideți Eclipse Modeling Tools.
   * Extindeți `flashcard_management.ecore`.
   * Arătați pachetul rădăcină (cu `Ns URI`), enum-ul `ApprovalStatus`, cele 3 clase (`EClass`) și relațiile de containment (`cards` și `citations`).
2. **Arătați Componenta din Python**:
   * Deschideți `flashcard_management.py` în VS Code.
   * Menționați că s-a utilizat **PyEcore** pentru a asigura interoperabilitatea cu standardul EMF direct în backend-ul de Python.
   * Rulați scriptul în terminalul integrat pentru a arăta generarea în timp real.
3. **Arătați Fișierul XMI Rezultat**:
   * Deschideți `sample_deck_instance.xmi` și arătați structura XML generată conform constrângerilor din metamodel.