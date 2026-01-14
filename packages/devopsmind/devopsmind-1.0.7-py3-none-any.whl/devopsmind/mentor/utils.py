def confidence_label(count: int) -> str:
    if count == 0:
        return "🌱 Unexplored"
    if count == 1:
        return "🧩 Emerging"
    if count == 2:
        return "🧠 Familiar"
    if count == 3:
        return "🏗️ Working"
    return "🧘 Confident"
