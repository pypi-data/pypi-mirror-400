AMBIGUOUS_TERMS = {
    "top": "ranking metric is unclear",
    "best": "definition of best is unclear",
    "highest": "metric is unclear",
    "lowest": "metric is unclear",
}

RESOLUTION_KEYWORDS = [
    "by total",
    "by amount",
    "by sum",
    "by count",
    "by number",
    "by purchase",
    "by sales"
]

def is_resolved(query: str) -> bool:
    query_lower = query.lower()
    return any(keyword in query_lower for keyword in RESOLUTION_KEYWORDS)

def detect_ambiguity(query: str):
    query_lower = query.lower()
    found = []

    for term, reason in AMBIGUOUS_TERMS.items():
        if term in query_lower and not is_resolved(query_lower):
            found.append({
                "term": term,
                "reason": reason
            })

    return found


def build_clarification(ambiguities: list) -> str:
    messages = []

    for item in ambiguities:
        term = item["term"]

        if term in ["top", "best", "highest", "lowest"]:
            messages.append(
                "Please specify the metric for ranking (e.g. total amount, count)."
            )
        elif term in ["recent", "latest"]:
            messages.append(
                "Please specify the time range (e.g. last 7 days, last month)."
            )

    return " ".join(messages)
