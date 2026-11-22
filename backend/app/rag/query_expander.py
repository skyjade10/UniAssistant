
def expand_query(question: str) -> str:

    q = question.lower()

    expansion_terms = []

    # Location and address intent
    location_terms = [
        "where",
        "location",
        "located",
        "address",
        "contact",
        "campus",
        "situated"
    ]

    if any(term in q for term in location_terms):
        expansion_terms.extend([
            "physical address",
            "postal address",
            "street address",
            "road",
            "city",
            "campus location",
            "contact details"
        ])

    # Academic programme intent
    programme_terms = [
        "programme",
        "programmes",
        "degree",
        "course",
        "courses"
    ]

    if any(term in q for term in programme_terms):
        expansion_terms.extend([
            "full-time degree programmes",
            "open and distance learning programmes",
            "evening degree programmes"
        ])

    if not expansion_terms:
        return question

    return "\n".join([
        question,
        *expansion_terms
    ])
