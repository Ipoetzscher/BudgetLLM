from memory import load_memory, save_memory


def test_save_and_load_memory_uses_temporary_file(tmp_path):
    test_file = tmp_path / "memory.json"
    original_memory = {
        "EXAMPLE MERCHANT": {
            "categories": ["Goods"],
            "ambiguous": False,
        }
    }

    save_memory(original_memory, test_file)

    assert load_memory(test_file) == original_memory
