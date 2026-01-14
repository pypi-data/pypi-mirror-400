# MASTER DESIGN : PREFLIGHTS

**Produit :** Preflights
**Site :** preflights.org
**Version :** 1.0.0
**Philosophie :** "Code Less, Specify More."
**Rôle :** Moteur de clarification et de capture de décisions pour le développement assisté par IA.

---

## 1. Le Problème

Les agents IA de code (Claude Code, Cursor, Windsurf) implémentent extrêmement vite.
Le problème n'est pas la vitesse, mais **ce qui est implémenté sans avoir été décidé explicitement**.

Cela produit :
- décisions architecturales implicites
- incohérences multi-fichiers
- rework déguisé en itérations rapides
- dette technique difficilement traçable

**Le vrai problème** :
un manque de contexte architectural explicite et une confusion entre décisions durables et intentions ponctuelles.

---

## 2. La Proposition

Preflights sépare explicitement trois activités que les outils IA mélangent :
1. **Décider** (architecture)
2. **Spécifier** (intention implémentable)
3. **Implémenter** (code)

Preflights ne génère pas de code.
Il force la clarification, documente les décisions, et produit des briefs clairs pour l'implémentation par un agent IA.

---

## 3. Modèle Conceptuel Global

### 3.1 Les Trois Artefacts

```
┌──────────────────────────────────────────────┐
│ ADR — Architecture Decision Records          │
│ • Décisions structurantes                    │
│ • Durables                                   │
│ • Peu nombreuses (mais historiques)          │
└──────────────────────────────────────────────┘
                      ↓
┌──────────────────────────────────────────────┐
│ TASK — Execution Briefs                      │
│ • Intentions ponctuelles                     │
│ • Scope local                                │
│ • Toujours implémentables                    │
└──────────────────────────────────────────────┘
                      ↓
┌──────────────────────────────────────────────┐
│ CODE                                         │
│ • Implémentation concrète                    │
│ • Respecte ADR + TASK                        │
└──────────────────────────────────────────────┘
```

### 3.2 Distinction des Natures

| Artefact | Durée | Portée | Réversibilité | Rôle |
|----------|-------|--------|---------------|------|
| ADR | Long terme | Globale | Difficile | Décider |
| TASK | Court terme | Locale | N/A | Spécifier |
| Code | Variable | Technique | Totale | Implémenter |

**Règle heuristique :**
Si changer implique une migration, une refonte, ou affecte de nombreuses parties du code → ADR.
Sinon → TASK.

---

## 4. Organisation des Artefacts

### 4.1 Arborescence Canonique

```
docs/
├── ARCHITECTURE_STATE.md      # Projection générée (lecture rapide)
├── CURRENT_TASK.md            # Tâche active (mutable, scope courant)
├── adr/
│   ├── 001_initial_architecture.md
│   ├── 042_authentication_strategy.md
│   └── ...
└── archive/
    └── task/
        ├── 001_initial_setup.md
        └── ...
```

### 4.2 Règles

- Les fichiers ADR sont **immutables** et ordonnés numériquement
- Chaque ADR représente un **snapshot complet** de l'architecture à un instant T
- `ARCHITECTURE_STATE.md` est une **projection générée automatiquement**
- Une seule TASK active à la fois : `CURRENT_TASK.md`
- L'ancienne TASK est archivée automatiquement lors de la création d'une nouvelle

---

## 5. Format ADR

Chaque ADR contient deux sections :
- **PART 1 : ARCHITECTURE SNAPSHOT** — Référence rapide (machine + humain)
- **PART 2 : DECISION DETAILS** — Justification et audit

### 5.1 Template ADR

```markdown
# ADR-XXX: [Titre de la décision]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PART 1: ARCHITECTURE SNAPSHOT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**Version:** XXX
**UID:** YYYYMMDDTHHMMSS.mmmZ
**Date (UTC):** YYYY-MM-DD
**Previous UID:** YYYYMMDDTHHMMSS.mmmZ | None

## Changes in this version
- [Added/Modified/Removed]: [Description]

## CURRENT ARCHITECTURE STATE

### Frontend
- Framework: [Decision] (ADR-XXX)
- State Management: [Decision] (ADR-XXX)
...

### Backend
- Language: [Decision] (ADR-XXX)
- Framework: [Decision] (ADR-XXX)
...

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PART 2: DECISION DETAILS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## Context
[Why is this decision needed?]

## Decision
[What did we decide?]

## Rationale
[Why this decision?]

## Alternatives Considered
...

## Consequences
...
```

### 5.2 Génération Déterministe

Les snapshots ADR sont reconstruits de manière déterministe :
- À partir du snapshot précédent + diff de la décision courante
- Validation automatique des catégories et champs
- Refus en cas d'incohérence

---

## 6. TASK — Execution Brief

Un `TASK.md` décrit **ce qui doit être implémenté maintenant**.

Contenu obligatoire :
- Objectif
- Contexte (ADR applicables)
- Allowlist / Forbidden list
- Contraintes techniques
- Acceptance Criteria

---

## 7. Architecture Technique

### 7.1 Structure du Code

```
preflights/
├── core/           # Logique pure (stateless, déterministe, NO I/O)
├── application/    # Orchestration (PreflightsApp, ports)
├── adapters/       # I/O (filesystem, LLM, sessions, UID, clock)
├── cli/            # Interface CLI (Click)
└── mcp/            # Serveur MCP
```

### 7.2 Ports & Adapters

| Couche | Responsabilité | I/O |
|--------|----------------|-----|
| `core/` | Logique métier pure | **NON** |
| `application/` | Orchestration | Via adapters |
| `adapters/` | I/O (FS, LLM, UID, Clock) | **OUI** |
| `cli/` | Interface utilisateur | Via adapters |
| `mcp/` | JSON-RPC MCP | Via adapters |

### 7.3 Ports Définis

| Port | Responsabilité |
|------|----------------|
| `LLMPort` | Génération de questions, extraction de DecisionPatch |
| `SessionPort` | Stockage des sessions avec TTL |
| `FilesystemPort` | Lecture/écriture des artefacts |
| `UIDProviderPort` | Génération d'identifiants |
| `ClockPort` | Horodatage |
| `FileContextBuilderPort` | Scan du repository |
| `ConfigLoaderPort` | Chargement de la configuration |

### 7.4 Règle Absolue : Core Pur

```python
# INTERDIT dans core/
datetime.now()          # Non-déterministe
open("file.txt")        # I/O
uuid.uuid4()            # Random
import anthropic        # Service externe
```

---

## 8. Workflow Canonique

### 8.1 Golden Path — CLI First

```bash
pf start "Add authentication"
# Clarification interactive
# → CURRENT_TASK.md généré
# → ADR généré si décision structurante
```

### 8.2 Fallback — MCP

Si l'utilisateur commence dans Claude Code :
- Claude détecte une requête ambiguë
- Appelle `require_clarification` via MCP
- Preflights génère les artefacts
- Claude reprend l'implémentation

### 8.3 Tools MCP

- `require_clarification` — Clarification et génération TASK/ADR
- `read_architecture` — Lecture de `ARCHITECTURE_STATE.md`

---

## 9. Boucle de Clarification

### 9.1 Flux Conceptuel

```
1. INPUT
   ├── Intention utilisateur
   ├── État de session (questions/réponses)
   └── Contexte filtré et redacté

2. LLM → OUTPUT STRUCTURÉ
   ├── questions[] (1..N)
   ├── missing_info[] (clés sémantiques, 1:1 avec questions)
   ├── decision_hint (task | adr | unsure)
   └── progress (0.0 à 1.0)

3. PREFLIGHTS
   ├── Affiche les questions
   ├── Collecte les réponses
   └── Met à jour l'état

4. STOP CONDITION
   └── missing_info vide → génération déterministe
```

### 9.2 Types de Réponse

```python
@dataclass(frozen=True)
class LLMResponse:
    """Réponse structurée du LLM."""
    questions: tuple[Question, ...]
    missing_info: tuple[str, ...]  # Clés sémantiques (1:1 avec questions)
    decision_hint: Literal["task", "adr", "unsure"]
    progress: float  # 0.0 à 1.0
```

### 9.3 Sémantique des Champs

| Champ | Rôle | Usage |
|-------|------|-------|
| `questions[]` | Questions user-facing | Affichage CLI/MCP |
| `missing_info[]` | Clés sémantiques stables | Tracking cross-session, progression |
| `decision_hint` | Indication non contraignante | Informatif uniquement |
| `progress` | Estimation de complétion | Affichage progression |

**Règle critique** : `decision_hint` est purement informatif. La décision TASK vs ADR est prise par le Core de manière déterministe.

---

## 10. LLM Provider & Credentials (BYOK)

### 10.1 Principe

Preflights est **open-source et gratuit** :
- Aucun modèle LLM managé
- Aucune facturation d'usage
- L'utilisateur fournit ses credentials (Bring Your Own Key)

### 10.2 Configuration

**Variables d'environnement** :

| Variable | Valeurs | Description |
|----------|---------|-------------|
| `PREFLIGHTS_LLM_PROVIDER` | `mock` \| `anthropic` \| `openai` \| `openrouter` | Provider à utiliser (default: `mock`) |
| `PREFLIGHTS_LLM_MODEL` | string | Modèle spécifique (optionnel) |

**Credentials** (priorité aux variables préfixées) :

| Provider | Variables (par ordre de priorité) |
|----------|-----------------------------------|
| Anthropic | `PREFLIGHTS_ANTHROPIC_API_KEY`, `ANTHROPIC_API_KEY` |
| OpenAI | `PREFLIGHTS_OPENAI_API_KEY`, `OPENAI_API_KEY` |
| OpenRouter | `PREFLIGHTS_OPENROUTER_API_KEY`, `OPENROUTER_API_KEY` |

### 10.3 Règles de Sécurité

- Credentials chargés uniquement depuis l'environnement local
- **Jamais** stockés ni journalisés
- Si absents : fallback vers `mock` ou erreur si `--llm-strict`

### 10.4 Implémentation (Adapter Pattern)

| Adapter | Comportement |
|---------|--------------|
| `MockLLMAdapter` | Déterministe (keywords/rules), default et fallback |
| `AnthropicLLMAdapter` | Tool use, modèle: `claude-sonnet-4-20250514` |
| `OpenAILLMAdapter` | Function calling, modèle: `gpt-4o` |
| `OpenRouterLLMAdapter` | API OpenAI-compatible |

### 10.5 Structured Output

Le LLM doit produire des sorties **strictement structurées** :
- **Anthropic** : Tool use
- **OpenAI / OpenRouter** : Function calling
- JSON brut = fallback technique uniquement

---

## 11. Contexte Envoyé au LLM

### 11.1 Principe de Minimisation

Preflights ne transmet **jamais** le workspace brut.

**Contenu autorisé** :
- Intention utilisateur
- État de session (questions posées, réponses)
- Titres des ADR et TASK existants (sans contenu)
- Outline des templates attendus
- Résumé de l'arborescence (haut niveau)

**Toujours exclus** :
- `.env*`, secrets, clés, tokens
- Logs, dumps, exports
- Données personnelles

### 11.2 Redaction Automatique

Patterns redactés par défaut :
- API keys (sk-*, AKIA*, etc.)
- JWT tokens
- Emails
- Secrets génériques (`password=`, `token=`, etc.)

Tout contenu sensible → `[REDACTED]`

### 11.3 Type LLMContext

```python
@dataclass(frozen=True)
class LLMContext:
    """Contexte filtré et redacté pour le LLM."""
    file_summary: str  # Résumé haut niveau (pas de paths bruts)
    technology_signals: tuple[tuple[str, str], ...]  # (type, valeur)
    architecture_summary: str | None  # Décisions existantes
```

---

## 12. Robustesse et Fallback

### 12.1 Paramètres

| Paramètre | Valeur |
|-----------|--------|
| Timeout par appel | 15 secondes |
| Max retries | 2 |
| Fallback | MockLLMAdapter |

### 12.2 Comportement de Fallback

```
LLM Error → Retry (max 2) → Fallback MockLLM + Warning visible
```

**Règles** :
- Fallback **jamais silencieux** : warning explicite affiché
- Mode `--llm-strict` : erreur explicite, pas de fallback

### 12.3 CLI Flags

| Flag | Comportement |
|------|--------------|
| (aucun) | Mock par défaut |
| `--llm` | Active le provider configuré |
| `--llm-strict` | Échec si erreur LLM (pas de fallback) |
| `--llm-provider <name>` | Override du provider |

---

## 13. Types Core

### 13.1 Question

```python
@dataclass(frozen=True)
class Question:
    id: str
    type: Literal["single_choice", "multi_choice", "free_text"]
    question: str
    options: tuple[str, ...] | None = None
    optional: bool = False
    depends_on_question_id: str | None = None  # Visibilité conditionnelle
    depends_on_value: str | None = None
```

### 13.2 DecisionPatch

```python
@dataclass(frozen=True)
class DecisionPatch:
    """Patch structuré pour l'architecture."""
    category: str  # Authentication, Database, Frontend, etc.
    fields: tuple[tuple[str, str], ...]  # (field_key, value)
```

### 13.3 Session

```python
@dataclass
class Session:
    id: str
    repo_path: str
    intention: str
    created_at: float
    expires_at: float  # TTL: 30 minutes

    asked_questions: tuple[Question, ...] = ()
    answers: dict[str, str | tuple[str, ...]] = field(default_factory=dict)

    # LLM tracking
    missing_info: tuple[str, ...] = ()
    decision_hint: str | None = None
    llm_provider_used: str | None = None
    llm_fallback_occurred: bool = False
```

---

## 14. Distribution

### 14.1 Installation

```bash
# Recommandé
uvx preflights start "Add authentication"

# Alternatives
pipx install preflights
pip install preflights
```

### 14.2 Dépendances Optionnelles

```bash
# Pour utiliser Anthropic
pip install preflights[anthropic]

# Pour utiliser OpenAI/OpenRouter
pip install preflights[openai]

# Tous les providers
pip install preflights[llm]
```

---

## 15. Métriques (MVP)

### 15.1 Hypothèse

Preflights réduit le rework en forçant la clarification.

### 15.2 Métriques Prioritaires

1. **Nombre d'itérations par feature** — Objectif: ≤ 2 (baseline: 3-4)
2. **Temps intention → PR merged** — Objectif: ≤ 15 min (baseline: 35 min)
3. **Couverture décisions documentées** — Objectif: ≥ 80%
4. **Taux de violations de scope** — Objectif: ≤ 10%

---

## 16. Principes Fondamentaux

| Principe | Description |
|----------|-------------|
| **LLM = Clarification** | Le LLM propose, ne décide jamais |
| **Core = Autorité** | Toute décision finale est déterministe |
| **Déterminisme** | Same inputs → Same outputs |
| **Sécurité** | Jamais de secrets transmis au LLM |
| **Résilience** | Fallback visible, jamais silencieux |
| **BYOK** | Aucun service payant, l'utilisateur amène ses clés |

---

## 17. Résumé

Preflights transforme :

```
Intention floue → Implémentation arbitraire → Dette
```

En :

```
Intention floue → Clarification → Décisions explicites → Implémentation alignée
```

Il ne ralentit pas le développement.
Il évite de prendre de mauvaises décisions trop trop.
