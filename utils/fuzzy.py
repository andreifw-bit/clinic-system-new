"""Utilitário para correspondência aproximada de nomes (case-insensitive, substring)."""

def fuzzy_match(query, options):
    """
    Dado um query digitado pelo usuário, retorna o item de `options`
    que melhor corresponde (case-insensitive, por prefixo ou substring).
    Retorna None se nenhuma correspondência for encontrada.
    """
    q = query.strip().lower()
    # 1) Correspondência exata (case-insensitive)
    for opt in options:
        if opt.lower() == q:
            return opt
    # 2) Começa com o que foi digitado
    for opt in options:
        if opt.lower().startswith(q):
            return opt
    # 3) O digitado está contido no nome
    for opt in options:
        if q in opt.lower():
            return opt
    # 4) O nome está contido no digitado
    for opt in options:
        if opt.lower() in q:
            return opt
    return None
