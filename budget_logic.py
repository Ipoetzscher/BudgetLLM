import csv
from io import StringIO

from memory import normalize_merchant
from model_client import make_llm_call


CATEGORIES_LIST = [
    "F&B", "Clothing", "HBA", "Goods", "Events/Services", "Other",
    "Dog", "Uber", "Parent T&E", "Lend/Borrow", "Inc/Allow"
]


def extract_month(date):
    return date.split("/")[0]


def check_memory(merchant_normalized, memory):
    if merchant_normalized in memory:
        if not memory[merchant_normalized]["ambiguous"]:
            return False, memory[merchant_normalized]["categories"]
        else:
            return True, memory[merchant_normalized]["categories"]
    else:
        return True, None


def process_chase_csv(file, start_id=1):
    text_file = StringIO(file.getvalue().decode("utf-8"))
    reader = csv.DictReader(text_file)
    count = start_id
    transactions = []

    for row in reader:
        date = row["Transaction Date"]
        merchant = row["Description"]
        amt = row["Amount"]
        cat = row["Category"]

        transaction = {}
        transaction["id"] = count
        transaction["month"] = extract_month(date)
        transaction["account"] = "CC"
        transaction["date"] = date
        transaction["merchant"] = merchant
        merchant_normalized, prefix = normalize_merchant(merchant, transaction["account"])
        transaction["merchant_normalized"] = merchant_normalized
        transaction["prefix"] = prefix
        transaction["total"] = float(amt)
        transaction["pre_categorization"] = cat
        transaction["allocations"] = [{"category": "TBD", "amount": 0}]
        transaction["description"] = ""
        transactions.append(transaction)
        transaction["merchant_ambiguous"] = True
        count += 1

    return transactions


def process_wells_fargo_csv(file, start_id=1):
    text_file = StringIO(file.getvalue().decode("utf-8"))
    reader = csv.DictReader(text_file)
    count = start_id
    transactions = []

    for row in reader:
        date = row["DATE"]
        merchant, prefix = normalize_merchant(row["DESCRIPTION"], "WF")

        transaction = {}
        transaction["id"] = count
        transaction["month"] = extract_month(date)
        transaction["account"] = "WF"
        transaction["date"] = date
        transaction["merchant"] = merchant
        transaction["merchant_normalized"] = merchant
        transaction["prefix"] = prefix
        transaction["total"] = float(row["AMOUNT"])
        transaction["pre_categorization"] = ""
        transaction["allocations"] = [{"category": "TBD", "amount": 0}]
        transaction["description"] = ""
        transaction["merchant_ambiguous"] = True
        transactions.append(transaction)
        count += 1

    return transactions


def process_uploaded_files(cc_file=None, wf_file=None):
    chase_transactions = process_chase_csv(cc_file) if cc_file is not None else []
    wf_start_id = len(chase_transactions) + 1
    wells_fargo_transactions = (
        process_wells_fargo_csv(wf_file, start_id=wf_start_id)
        if wf_file is not None
        else []
    )
    return chase_transactions + wells_fargo_transactions


def allocate(transaction, memory, categorize=make_llm_call):
    merchant_normalized = transaction["merchant_normalized"]
    bank_description = transaction["pre_categorization"]
    total = transaction["total"]
    prefix = transaction["prefix"]
    ambiguous, categories = check_memory(merchant_normalized, memory)

    if not ambiguous:
        transaction["allocator"] = "Memory"
        transaction["needs_review"] = False
        category = categories[0]
        prefix = transaction["prefix"]
    else:
        transaction["allocator"] = "LLM"
        transaction["needs_review"] = True
        category = categorize(merchant_normalized, bank_description, total, prefix)
        if category not in CATEGORIES_LIST:
            category = "Other"

    transaction["allocations"] = [{"category" : category, "amount" : total}]
    return transaction


def build_review_queue(transactions):
    return [transaction for transaction in transactions if transaction["needs_review"]]


def process_edits(memory, allocated_transactions, edited_changes):
    condensed_dict = {}

    for transaction in edited_changes:
        condensed_dict[transaction["id"]] = transaction["category"]
        merchant_normalized = transaction["merchant_normalized"]
        if merchant_normalized in memory:
            if transaction["category"] not in memory[merchant_normalized]["categories"]:
                memory[merchant_normalized]["categories"].append(transaction["category"])
        else:
            memory[merchant_normalized] = {}
            memory[merchant_normalized]["categories"] = [transaction["category"]]
        memory[merchant_normalized]["ambiguous"] = transaction["merchant_ambiguous"]

    for transaction in allocated_transactions:
        if transaction["needs_review"]:
            transaction["needs_review"] = False
            transaction_id = transaction["id"]
            updated_category = condensed_dict[transaction_id]
            transaction["allocations"][0] = {
                "category" : updated_category,
                "amount" : transaction["total"]
            }


def handle_split_rules(allocations):
    new_allocations = []
    parents_share = 0

    for allocation in allocations:
        category = allocation["category"]
        amount = allocation["amount"]
        if category in ["Dog", "Uber"]:
            my_share = round(amount * 0.25, 2)
            parents_share += amount - my_share
            new_allocations.append({"category": category, "amount": my_share})
        else:
            new_allocations.append(allocation.copy())

    if parents_share != 0:
        new_allocations.append({"category": "Parent T&E", "amount": parents_share})

    return new_allocations


def create_left_output(transactions):
    output = StringIO()
    writer = csv.DictWriter(
        output,
        fieldnames=["month", "account", "date", "merchant", "description", "total"],
        delimiter="\t",
        extrasaction="ignore"
    )
    writer.writerows(transactions)
    return output.getvalue()


def create_right_output(transactions):
    new_list = []

    for transaction in transactions:
        output_allocations = handle_split_rules(transaction["allocations"])
        new_dict = {}
        for allocation in output_allocations:
            category = allocation["category"]
            amount = allocation["amount"]
            new_dict[category] = new_dict.get(category, 0) + amount
        new_list.append(new_dict)

    output = StringIO()
    writer = csv.DictWriter(
        output,
        fieldnames=CATEGORIES_LIST,
        delimiter="\t",
        extrasaction="ignore"
    )
    writer.writerows(new_list)
    return output.getvalue()
