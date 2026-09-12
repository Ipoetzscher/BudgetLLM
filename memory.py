import json
import os


def num_digits(word):
    count = 0
    for char in word:
        if char.isdigit():
            count += 1
    return count


def garbage(word):
    if num_digits(word) >= 3 or word == "-" or word == "STORE":
        return True

    return False


def load_memory(file_path="memory.json"):
    with open(file_path) as json_memory:
        memory = json.load(json_memory)
    return memory


def save_memory(memory, file_path="memory.json"):
    with open(file_path, "w") as json_memory:
        json.dump(memory, json_memory, indent=4)


def contains_family_marker(text):
    markers = os.getenv("BUDGET_FAMILY_MARKERS", "")
    family_markers = [
        marker.strip().upper()
        for marker in markers.split(",")
        if marker.strip()
    ]
    return any(marker in text for marker in family_markers)


def parse_WF(merchant):
    index_ref = merchant.find("REF #")
    if index_ref != -1:
        merchant = merchant[:index_ref]

    if merchant.startswith("MOBILE DEPOSIT"):
        return "MOBILE DEPOSIT"
    elif merchant.startswith("VENMO PAYMENT"):
        return "VENMO PAYMENT"
    elif merchant.startswith("PURCHASE AUTHORIZED ON"):
        words = merchant.split()
        return " ".join(words[4:-3])
    elif merchant.startswith("ZELLE FROM"):
        index_on = merchant.find(" ON ")
        if index_on != -1:
            sender = merchant[len("ZELLE FROM "):index_on]
            if contains_family_marker(sender):
                sender = "DAD"
            else:
                sender = "NOT DAD"
            return f"ZELLE FROM {sender}"
        else:
            return "ZELLE FROM IDK"
    elif merchant.startswith("ZELLE TO"):
        index_on = merchant.find(" ON ")
        if index_on != -1:
            recipient = merchant[len("ZELLE TO "):index_on]
            if contains_family_marker(recipient):
                recipient = "DAD"
            else:
                recipient = "NOT DAD"
            return f"ZELLE TO {recipient}"
        else:
            return "ZELLE TO IDK"
    else:
        keep = []
        words = merchant.split()
        for word in words:
            if len(keep) >= 4:
                break
            if word[0].isdigit() or word.startswith("XX") or contains_family_marker(word):
                continue
            else:
                keep.append(word)
        return " ".join(keep)


def parse_CC(merchant):
    prefix = None

    if merchant.startswith("SP "):
        merchant = merchant[3:]

    index_asterik = merchant.find("*")
    if index_asterik != -1:
        prefix = merchant[:index_asterik].strip()

        if "AMAZON" in prefix:
            if "PRIME" in prefix:
                return "AMAZON PRIME", None
            else:
                return "AMAZON MKTPL", None

        if "UBER" in prefix or "GOOGLE" in prefix:
            cleaned = merchant[:index_asterik] + merchant[index_asterik + 1:]
            return " ".join(cleaned.split()), None

        merchant = merchant[index_asterik + 1:]

    keep = []
    words = merchant.split()
    for word in words:
        if garbage(word):
            continue
        else:
            if word.endswith(".COM"):
                keep.append(word.removesuffix(".COM"))
            else:
                keep.append(word)

    return " ".join(keep), prefix


def normalize_merchant(merchant, account="CC"):
    index_amp = merchant.find("amp;")
    if index_amp != -1:
        merchant = merchant[:index_amp] + merchant[index_amp + 4:]
    merchant = merchant.upper()

    if account == "WF":
        parsed_merchant = parse_WF(merchant)
        if merchant.startswith("PURCHASE AUTHORIZED ON"):
            return parse_CC(parsed_merchant)
        return parsed_merchant, None

    if account == "CC":
        return parse_CC(merchant)

    return merchant, None
