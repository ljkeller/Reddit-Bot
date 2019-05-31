def search_keywords(keywords: list, comment_body: str):
    for keyword in keywords:
        if keyword in comment_body:
            return keyword

    return None
