
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
        "program",
        "programme",
        "degree",
        "course",
        "offer",
        "study",
        "studies",
        "learn",
        "available",
        "bachelor",
        "diploma",
        "certificate",
        "qualification"
    ]

    if any(term in q for term in programme_terms):
        expansion_terms.extend([
            "Certificate",
            "Diploma",
            "Degree",
            "Masters",
            "Bachelor of",
            "Full-time degree programmes",
            "Open and distance learning programmes",
            "Evening programmes",
            "Information Technology",
            "Business Administration",
            "Electrical",
            "Course Code"
        ])

    if not expansion_terms:
        return question

    return "\n".join([
        question,
        *expansion_terms
    ])
