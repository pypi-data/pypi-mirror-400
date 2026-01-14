# "Other (specify)" Specification

**Product:** Preflights
**Version:** 1.0.0
**Purpose:** Define the canonical handling of "Other (specify)" options in choice questions

---

## Vision commune (validée)

UX (ce que voit l’utilisateur)

Pour toutes les questions de type QCM (single_choice ou multi_choice) :

Question: Which authentication strategy do you want to use?

○ OAuth
○ Email/Password
○ Magic Link
○ Other (specify): [_____________________]

	•	Tant que Other n’est pas sélectionné → le champ texte est caché / désactivé
	•	Dès que Other est sélectionné → le champ texte apparaît automatiquement
	•	Pour l’utilisateur :
	•	c’est une seule question
	•	c’est fluide
	•	aucune notion de “question cachée”

Modèle mental côté système (important)

Même si l’UX est “une seule question”, le modèle reste volontairement explicite :
•	Question visible :
{
"id": "auth_strategy",
"type": "single_choice",
"options": ["OAuth", "Email/Password", "Magic Link", "Other (specify)"]
}

	•	Question cachée (logique, pas UX) :
{
"id": "auth_strategy_other",
"type": "free_text",
"optional": true,
"depends_on": {
"question_id": "auth_strategy",
"value": "Other (specify)"
}
}

Où ça vit dans l’architecture (très important)

✅ Core
•	Ne change pas
•	Il reçoit des réponses normalisées
•	Il ne sait même pas que “Other” existait

✅ Application / LLMAdapter
•	Ajoute systématiquement Other (specify) aux QCM
•	Génère la question _other associée
•	Gère la logique conditionnelle

✅ CLI / UI
•	Gère l’affichage conditionnel
•	Mappe automatiquement :

{
"auth_strategy": "Other (specify)",
"auth_strategy_other": "SAML via Okta"
}


## NORMATIVE — “Other (specify)” for choice questions

- Every `single_choice` and `multi_choice` question MUST include the canonical option value: `"Other (specify)"`.
- For each such question `<qid>`, the system MUST define an associated free-text field `<qid>__other` (type `free_text`).
- Conditional requirement:
    - If answer `<qid>` includes `"Other (specify)"`, then `<qid>__other` MUST be present and non-empty.
    - Otherwise, `<qid>__other` MUST be omitted (or ignored if provided).
- i18n:
    - UI labels may be localized, but the payload value MUST remain `"Other (specify)"` (canonical) across all locales.