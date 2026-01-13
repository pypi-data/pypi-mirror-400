def generate_fix_text(links: list[dict], fix_link_label: str) -> str:
    if not links:
        return ""
    output = f"\n## {fix_link_label}\n"

    for link in links:
        output += f"- [{link['title']}]({link['url']})\n"

    return output
