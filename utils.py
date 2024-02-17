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

# def group_bets(json_data, new_bet_data=None):
#     # Group by marketId
#     grouped_data = {}
#     for oc_bet_id, bet_data in json_data.items():
#         market_id = bet_data["marketId"]
#         if market_id not in grouped_data:
#             grouped_data[market_id] = []
#         cut_bet_data = {
#             "ocBetId": bet_data["ocBetId"],
#             "betName": bet_data["betName"]
#         }
#         grouped_data[market_id].append(cut_bet_data)
#
#     if new_bet_data:
#         for bet_id, bet_data in new_bet_data.items():
#             print(bet_id, bet_data)
#             decimal_odd = bet_data.get("decimal")
#
#             # Find the corresponding ocBetId in the grouped data
#             for market_id, market_bets in grouped_data.items():
#                 for oc_bet_data in market_bets:
#                     if oc_bet_data["ocBetId"] == int(bet_id):
#                         # Add the decimal odd to the existing data
#                         oc_bet_data["decimal"] = decimal_odd
#                         oc_bet_data["bookmakerCodes"] = bet_data["bookmakerCodes"]
#
#     # Create a new dictionary with only valid items
#     grouped_data = {key: value for key, value in grouped_data.items() if all('decimal' in item for item in value)}
#
#
#     # Convert the grouped data dictionary back to JSON
#     grouped_json_data = json.dumps(grouped_data, indent=2)
#
#     # Specify the file path where you want to save the grouped JSON data
#     grouped_file_path = 'grouped_output.json'
#
#     # Write the grouped JSON data to the file
#     with open(grouped_file_path, 'w') as grouped_json_file:
#         grouped_json_file.write(grouped_json_data)
#
#     print(f"Grouped JSON data has been written to {grouped_file_path}")
