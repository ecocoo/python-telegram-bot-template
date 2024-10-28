BOOK_PATH = 'book/Witcher_part_1.txt'
PAGE_SIZE = 1050

book = {}


def _get_page_text(text, start, size):
    end = start + size
    if end > len(text):
        end = len(text)
    return text[start:end].strip(), end - start


def prepare_book(path):
    with open(path, 'r', encoding='utf-8') as file:
        text = file.read()
    start, page_number = 0, 1
    while start < len(text):
        page_text, page_size = _get_page_text(text, start, PAGE_SIZE)
        book[page_number] = page_text
        start += page_size
        page_number += 1


prepare_book(BOOK_PATH)