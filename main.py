import streamlit as st
from st_copy import copy_button

from budget_logic import (
    CATEGORIES_LIST,
    allocate,
    build_review_queue,
    create_left_output,
    create_right_output,
    process_edits,
    process_uploaded_files,
)
from memory import load_memory, save_memory


# Transaction dictionary keys
#     transaction["id"] : Int
#     transaction["month"] : String
#     transaction["account"] : "CC" or "WF"
#     transaction["date"] : String
#     transaction["merchant"] : String
#     transaction["total"] : Float
#     transaction["pre_categorization"] : String # empty when unavailable
#     transaction["allocations"] : [{"category" : String, "amount" : Float}]
#     transaction["merchant_normalized"] : String
#     transaction["prefix"] : String
#     transaction["description"] : String
#     transaction["allocator"] : String
#     transaction["needs_review"] : Bool
#     transaction["merchant_ambiguous"] : Bool


def process_uploaded_transactions():
    memory = st.session_state["memory"]
    transactions = process_uploaded_files(cc_file, wf_file)

    allocated_transactions = []
    for transaction in transactions:
        allocated_transactions.append(allocate(transaction, memory))

    return allocated_transactions


# UI
st.title("Budget Allocator")
st.subheader("Upload your transactions")
cc_file = st.file_uploader("Select CC file", type="csv", key="cc")
wf_file = st.file_uploader("Select Wells Fargo file", type="csv", key="wf")


if "memory" not in st.session_state:
    st.session_state["memory"] = load_memory()

if "transactions" not in st.session_state:
    st.session_state["transactions"] = None

if (cc_file is not None or wf_file is not None) and st.button("Process transactions"):
    st.session_state["transactions"] = process_uploaded_transactions()


if st.session_state["transactions"] is not None:
    allocated_transactions = st.session_state["transactions"]
    to_review = build_review_queue(allocated_transactions)

    if to_review:
        st.subheader("Please review these transactions")

        to_review_flattened = []
        for transaction in to_review:
            flattened = transaction.copy()
            flattened["category"] = transaction["allocations"][0]["category"]
            to_review_flattened.append(flattened)

        edited_changes = st.data_editor(
            to_review_flattened,
            column_order=[
                "account",
                "date",
                "merchant",
                "merchant_normalized",
                "total",
                "category",
                "merchant_ambiguous",
            ],
            disabled=["account", "date", "merchant", "total", "allocator"],
            column_config={
                "account": "Acc",
                "date": "Date",
                "merchant": "Merchant",
                "merchant_normalized": "Abrev",
                "total": "Amt",
                "category": st.column_config.SelectboxColumn(
                    "Category",
                    help="The category",
                    options=CATEGORIES_LIST,
                    required=True,
                ),
                "id": None,
                "allocator": None,
                "month": None,
                "pre_categorization": None,
                "needs_review": None,
                "prefix": None,
                "description": None,
                "allocations": None,
                "merchant_ambiguous": "Ambiguous?",
            },
        )

        if st.button("Confirm Changes"):
            memory = st.session_state["memory"]
            process_edits(memory, allocated_transactions, edited_changes)
            save_memory(memory)
            st.session_state["review_complete"] = True

    else:
        memory = st.session_state["memory"]
        save_memory(memory)
        st.session_state["review_complete"] = True

    if st.session_state.get("review_complete", False):
        transactions = st.session_state["transactions"]
        tsv_left_output = create_left_output(transactions)
        tsv_right_output = create_right_output(transactions)

        st.subheader("Done!")

        with st.expander("Copy left side"):
            st.code(tsv_left_output, language=None)

        with st.expander("Copy right side"):
            st.code(tsv_right_output, language=None)

        with st.container(
            horizontal=True,
            horizontal_alignment="distribute",
            vertical_alignment="center",
        ):
            with st.container(horizontal=True):
                st.write("Left side of spreadsheet")
                copy_button(tsv_left_output, tooltip="Copy", key="copy_left")
            with st.container(horizontal=True):
                st.write("Right side of spreadsheet")
                copy_button(tsv_right_output, tooltip="Copy", key="copy_right")
