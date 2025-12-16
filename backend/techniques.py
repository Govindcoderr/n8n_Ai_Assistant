def detect_techniques(intent: dict) -> list[str]:
    t = []

    if intent.get("schedule"):
        t.append("SCHEDULING")

    if intent.get("api"):
        t.append("DATA_EXTRACTION")

    if intent.get("ai_usage"):
        t.append("CONTENT_GENERATION")

    if intent.get("notification"):
        t.append("NOTIFICATION")

    return t
