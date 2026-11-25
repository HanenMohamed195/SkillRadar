def normalize_search_input(value: str) -> str:
    return value.strip().casefold()


def find_canonical_skill(user_input: str, taxonomy: dict):
    search_value = normalize_search_input(user_input)

    for canonical_skill, data in taxonomy.items():
        aliases = data.get("aliases", [])

        candidates = [canonical_skill, *aliases]

        if any(
            normalize_search_input(candidate) == search_value
            for candidate in candidates
        ):
            return canonical_skill

    return None