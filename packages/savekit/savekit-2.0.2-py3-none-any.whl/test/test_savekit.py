import os
from pydantic import BaseModel
from savekit import SaveKit


# Example Pydantic model
class User(BaseModel):
    id: int
    name: str

def run_tests():
    # Ensure the store folder exists

    # Initialize SaveKit (DB will be store/test.db)
    with SaveKit() as sk:
        print("=== Testing set_item ===")
        sk.set_item("integer", 42)
        sk.set_item("float", 3.14)
        sk.set_item("string", "Hello SaveKit")
        sk.set_item("list", [1, 2, 3])
        sk.set_item("dict", {"a": 1, "b": 2})
        sk.set_item("user", User(id=1, name="Luis"))

        print("=== Testing get_item ===")
        print("integer:", sk.get_item("integer"))
        print("float:", sk.get_item("float"))
        print("string:", sk.get_item("string"))
        print("list:", sk.get_item("list"))
        print("dict:", sk.get_item("dict"))
        # Retrieve as BaseModel
        user_obj = sk.get_item("user", model=User)
        print("user:", user_obj)
        print("user name:", user_obj.name)

        print("=== Testing get_all_items ===")
        all_items = sk.get_all_items()
        print(all_items)

        print("=== Testing delete_item ===")
        sk.delete_item("integer")
        print("integer after delete:", sk.get_item("integer", default="Not found"))

        print("=== Testing clear_store ===")
        sk.clear_store()
        print("all items after clear:", sk.get_all_items())

if __name__ == "__main__":
    run_tests()
