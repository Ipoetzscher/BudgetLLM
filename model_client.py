from openai import OpenAI


CATEGORIES_DICT = {
    "F&B" : "Food and beverage",
    "Clothing" : "Clothing and accessories",
    "HBA" : "Health and Beauty Aids - personal care, makeup, skincare, etc.",
    "Goods" : "Goods for the home, personal goods, pet goods, etc.",
    "Events/Services" : "Events and services including subscriptions, public transportation services (excluding Caltrain), movie/concert tickets",
    "Other" : "Other",
    "Dog" : "Vet & Grooming",
    "Uber" : "Uber, Waymo, Caltrain",
    "Parent T&E" : "Things my parents reimburse me for, which include groceries, medical expenses, gas, and dog food",
    "Lend/Borrow" : "When I pay for someone else",
    "Inc/Allow" : "Income (from employers) and allowance (from Dad)"
}

PROMPT = f"""
Categorize this transaction into exactly one of these categories: {CATEGORIES_DICT}, which is formatted as a dictionary with the category name and a brief description of what belongs in the category. 
First, see the attached context. 
Return only the category name and nothing else. 
"""

# takes in the needed context for the LLM, makes the call, and returns the response
def make_llm_call(description, bank_description, amount, prefix):
    transaction_info = f"""
    Merchant description: {description}
    Bank auto-categorization: {bank_description}
    Amount: {amount}
    Transaction Processor (if any): {prefix}
    """

    client = OpenAI()
    response = client.responses.create(
        model="gpt-5.6-luna",
        instructions=PROMPT,
        input=transaction_info,
    )
    return response.output_text.strip()
