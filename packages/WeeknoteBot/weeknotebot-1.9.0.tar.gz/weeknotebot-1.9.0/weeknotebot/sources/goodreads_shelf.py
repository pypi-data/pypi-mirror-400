import feedparser


def get_books_from_shelf(user_id, shelf_name_code, shelf_name_label):
    url = f"https://www.goodreads.com/review/list_rss/{user_id}?shelf={shelf_name_code}"
    output = []
    for element_link in feedparser.parse(url).entries:
        output.append(
            f"[![{element_link.title}]({element_link.book_medium_image_url})]({element_link.link}) "
        )

    output_str = ""

    if output:
        output_str += f"\n## {shelf_name_label}\n"
        for element in output:
            output_str += element
        output_str += "\n"

    return output_str
