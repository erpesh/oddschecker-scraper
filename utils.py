import json


def get_full_url(url: str):
    if url.startswith("http://") or url.startswith("https://"):
        return url
    return "https://www.oddschecker.com/" + url


def get_ajax_url(link: str, market: str):
    if "https://www.oddschecker.com/" in link:
        link = link.replace("https://www.oddschecker.com/", "")
    return f"https://www.oddschecker.com/ajax/cards-default/{link}?market={market}"


def split_list(input_list: list[str], max_chunk_size: int) -> list[list[str]]:
    # Calculate the number of chunks needed
    num_chunks = -(-len(input_list) // max_chunk_size)

    # Use a list comprehension to create the chunks
    chunks = [input_list[i * max_chunk_size:(i + 1) * max_chunk_size] for i in range(num_chunks)]

    return chunks

def write_json(file_name: str, content: object, **kwargs):
    with open(file_name, 'w') as json_file:
        json.dump(content, json_file, **kwargs)
        
def read_json(file_name: str):
    with open(file_name, 'r') as json_file:
        return json.load(json_file)