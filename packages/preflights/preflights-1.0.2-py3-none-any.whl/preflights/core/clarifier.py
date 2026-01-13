"""
Preflights Core Clarifier.

Pure logic for generating clarification questions.
No I/O.
"""

from __future__ import annotations

from preflights.core.types import (
    ArchitectureState,
    FileContext,
    HeuristicsConfig,
    Intention,
    Question,
)


# Maximum questions per clarification
MAX_QUESTIONS = 5


def generate_questions(
    intention: Intention,
    current_architecture: ArchitectureState | None,
    file_context: FileContext,
    heuristics_config: HeuristicsConfig,
    already_asked: frozenset[str],
) -> tuple[Question, ...]:
    """
    Generate clarification questions based on heuristics.

    Rules:
    - Max 5 questions
    - Never re-ask same question ID
    - Prefer choice questions over free-text
    - Questions grounded in schema + file_context signals

    Args:
        intention: User's intention
        current_architecture: Current architecture state (if exists)
        file_context: Repository topology
        heuristics_config: Configuration with keywords and schema
        already_asked: Set of question IDs already asked

    Returns:
        Tuple of questions (max 5)
    """
    questions: list[Question] = []
    intention_lower = intention.text.lower()

    # Detect which categories might be relevant
    detected_categories = _detect_categories(
        intention_lower, heuristics_config.category_keywords
    )

    # Generate questions for each detected category
    for category in detected_categories:
        if len(questions) >= MAX_QUESTIONS:
            break

        category_questions = _generate_category_questions(
            category,
            intention_lower,
            current_architecture,
            file_context,
            heuristics_config,
            already_asked,
        )

        for q in category_questions:
            if len(questions) >= MAX_QUESTIONS:
                break
            if q.id not in already_asked:
                questions.append(q)

    # If no category detected, generate generic questions
    if not questions and not detected_categories:
        generic_questions = _generate_generic_questions(
            intention_lower,
            file_context,
            already_asked,
        )
        questions.extend(generic_questions[:MAX_QUESTIONS])

    return tuple(questions)


def _detect_categories(
    intention_lower: str,
    category_keywords: tuple[tuple[str, tuple[str, ...]], ...],
) -> tuple[str, ...]:
    """
    Detect relevant categories from intention text.

    Returns categories sorted by number of keyword matches (descending).
    """
    scores: dict[str, int] = {}

    for cat_name, keywords in category_keywords:
        score = 0
        for keyword in keywords:
            if keyword in intention_lower:
                score += 1
        if score > 0:
            scores[cat_name] = score

    # Sort by score descending
    sorted_categories = sorted(scores.keys(), key=lambda k: scores[k], reverse=True)
    return tuple(sorted_categories)


def _generate_category_questions(
    category: str,
    intention_lower: str,
    current_architecture: ArchitectureState | None,
    file_context: FileContext,
    heuristics_config: HeuristicsConfig,
    already_asked: frozenset[str],
) -> list[Question]:
    """
    Generate questions for a specific category.

    Uses predefined question templates per category.
    """
    questions: list[Question] = []

    # Get fields for this category from schema
    category_fields: tuple[str, ...] = ()
    for cat_name, fields in heuristics_config.schema.categories:
        if cat_name.lower() == category.lower():
            category_fields = fields
            break

    # Generate questions based on category
    if category.lower() == "authentication":
        questions.extend(
            _auth_questions(category_fields, file_context, already_asked)
        )
    elif category.lower() == "database":
        questions.extend(
            _database_questions(category_fields, file_context, already_asked)
        )
    elif category.lower() == "frontend":
        questions.extend(
            _frontend_questions(category_fields, file_context, already_asked)
        )
    elif category.lower() == "backend":
        questions.extend(
            _backend_questions(category_fields, file_context, already_asked)
        )
    elif category.lower() == "infra":
        questions.extend(
            _infra_questions(category_fields, file_context, already_asked)
        )
    else:
        # Generic category questions
        questions.extend(
            _generic_category_questions(category, category_fields, already_asked)
        )

    return questions


def _auth_questions(
    fields: tuple[str, ...],
    file_context: FileContext,
    already_asked: frozenset[str],
) -> list[Question]:
    """Generate authentication-specific questions."""
    questions: list[Question] = []

    # Strategy question
    q_id = "auth_strategy"
    if q_id not in already_asked and "Strategy" in fields:
        questions.append(
            Question(
                id=q_id,
                type="single_choice",
                question="Which authentication strategy?",
                options=("OAuth", "Email/Password", "Magic Links", "SAML"),
            )
        )

    # Library question (depends on context)
    q_id = "auth_library"
    if q_id not in already_asked and "Library" in fields:
        # Detect if Next.js
        is_nextjs = _has_signal(file_context, "nextjs") or _has_path_pattern(
            file_context, "next.config"
        )
        if is_nextjs:
            options = ("NextAuth.js", "Clerk", "Auth0", "Custom")
        else:
            options = ("Passport.js", "Auth0", "Clerk", "Custom")

        questions.append(
            Question(
                id=q_id,
                type="single_choice",
                question="Which authentication library?",
                options=options,
            )
        )

    # OAuth providers (if OAuth likely)
    q_id = "oauth_providers"
    if q_id not in already_asked:
        questions.append(
            Question(
                id=q_id,
                type="multi_choice",
                question="Which OAuth providers to support?",
                options=("Google", "GitHub", "Microsoft", "Facebook"),
                min_selections=1,
                optional=True,
            )
        )

    return questions


def _database_questions(
    fields: tuple[str, ...],
    file_context: FileContext,
    already_asked: frozenset[str],
) -> list[Question]:
    """Generate database-specific questions."""
    questions: list[Question] = []

    # Type question
    q_id = "db_type"
    if q_id not in already_asked and "Type" in fields:
        questions.append(
            Question(
                id=q_id,
                type="single_choice",
                question="Which database type?",
                options=("PostgreSQL", "MySQL", "MongoDB", "SQLite"),
            )
        )

    # ORM question
    q_id = "db_orm"
    if q_id not in already_asked and "ORM" in fields:
        # Detect language/framework
        is_typescript = _has_path_pattern(file_context, ".ts")
        if is_typescript:
            options = ("Prisma", "TypeORM", "Drizzle", "None")
        else:
            options = ("SQLAlchemy", "Django ORM", "Sequelize", "None")

        questions.append(
            Question(
                id=q_id,
                type="single_choice",
                question="Which ORM to use?",
                options=options,
            )
        )

    return questions


def _frontend_questions(
    fields: tuple[str, ...],
    file_context: FileContext,
    already_asked: frozenset[str],
) -> list[Question]:
    """Generate frontend-specific questions."""
    questions: list[Question] = []

    # Framework question
    q_id = "frontend_framework"
    if q_id not in already_asked and "Framework" in fields:
        questions.append(
            Question(
                id=q_id,
                type="single_choice",
                question="Which frontend framework?",
                options=("React", "Vue", "Svelte", "Angular"),
            )
        )

    # Styling question
    q_id = "styling"
    if q_id not in already_asked and "Styling" in fields:
        questions.append(
            Question(
                id=q_id,
                type="single_choice",
                question="Which styling approach?",
                options=("Tailwind CSS", "CSS Modules", "Styled Components", "Plain CSS"),
            )
        )

    return questions


def _backend_questions(
    fields: tuple[str, ...],
    file_context: FileContext,
    already_asked: frozenset[str],
) -> list[Question]:
    """Generate backend-specific questions."""
    questions: list[Question] = []

    # Language question
    q_id = "backend_language"
    if q_id not in already_asked and "Language" in fields:
        questions.append(
            Question(
                id=q_id,
                type="single_choice",
                question="Which backend language?",
                options=("TypeScript/Node", "Python", "Go", "Rust"),
            )
        )

    # API style question
    q_id = "api_style"
    if q_id not in already_asked and "API_Style" in fields:
        questions.append(
            Question(
                id=q_id,
                type="single_choice",
                question="Which API style?",
                options=("REST", "GraphQL", "gRPC", "tRPC"),
            )
        )

    return questions


def _infra_questions(
    fields: tuple[str, ...],
    file_context: FileContext,
    already_asked: frozenset[str],
) -> list[Question]:
    """Generate infrastructure-specific questions."""
    questions: list[Question] = []

    # Hosting question
    q_id = "hosting"
    if q_id not in already_asked and "Hosting" in fields:
        questions.append(
            Question(
                id=q_id,
                type="single_choice",
                question="Which hosting platform?",
                options=("Vercel", "AWS", "GCP", "Self-hosted"),
            )
        )

    # Caching question
    q_id = "caching"
    if q_id not in already_asked and "Caching" in fields:
        questions.append(
            Question(
                id=q_id,
                type="single_choice",
                question="Which caching solution?",
                options=("Redis", "Memcached", "In-memory", "None"),
            )
        )

    return questions


def _generic_category_questions(
    category: str,
    fields: tuple[str, ...],
    already_asked: frozenset[str],
) -> list[Question]:
    """Generate generic questions for unknown categories."""
    questions: list[Question] = []

    for field in fields[:3]:  # Max 3 fields
        q_id = f"{category.lower()}_{field.lower()}"
        if q_id not in already_asked:
            questions.append(
                Question(
                    id=q_id,
                    type="free_text",
                    question=f"What value for {category}.{field}?",
                )
            )

    return questions


def _generate_generic_questions(
    intention_lower: str,
    file_context: FileContext,
    already_asked: frozenset[str],
) -> list[Question]:
    """Generate generic questions when no category detected."""
    questions: list[Question] = []

    # Ask about scope
    q_id = "scope"
    if q_id not in already_asked:
        questions.append(
            Question(
                id=q_id,
                type="free_text",
                question="Which files or directories should this change affect?",
            )
        )

    # Ask about acceptance criteria
    q_id = "acceptance_criteria"
    if q_id not in already_asked:
        questions.append(
            Question(
                id=q_id,
                type="free_text",
                question="How will we know this is complete? (acceptance criteria)",
            )
        )

    return questions


def _has_signal(file_context: FileContext, signal_key: str) -> bool:
    """Check if file context has a specific signal."""
    for key, _ in file_context.signals:
        if key.lower() == signal_key.lower():
            return True
    return False


def _has_path_pattern(file_context: FileContext, pattern: str) -> bool:
    """Check if any path contains a pattern."""
    pattern_lower = pattern.lower()
    for path in file_context.paths:
        if pattern_lower in path.lower():
            return True
    return False
