def expand_query(question: str) -> str:

    q = question.lower()

    if any(word in q for word in [
        "programme", "programmes",
        "degree", "course", "courses"
    ]):
        return f"""
        {question}

        ZUT academic programmes and qualifications.
        Undergraduate degree programmes.
        Full-time degree programmes.
        Evening degree programmes.
        Open and Distance Learning programmes.
        Bachelor of Information Technology.
        Bachelor of Cyber Security.
        Bachelor of Software Engineering.
        Bachelor of Business Administration.
        """

    return question