#!/usr/bin/env python3
import os
from fast_decision import FastDecision


def main():
    engine = FastDecision(os.environ['TEST_RULES_JSON_PATH'])

    # Test basic comparison operators
    print("=== TEST 1: $equals operator (Platinum tier) ===")
    data1 = {"user": {"tier": "Platinum"}, "transaction": {"amount": 100}}
    result1 = engine.evaluate_rules(data1, categories=["Pricing"])
    print(f"Result: {result1}")
    print(f"Expected: ['R1_Platinum']")
    print(f"Success: {result1[0].get('id') == 'R1_Platinum'}\n")

    print("=== TEST 2: $greater-than operator (High amount fraud) ===")
    data2 = {"user": {"tier": "Gold"}, "transaction": {"amount": 15000}}
    result2 = engine.evaluate_rules(data2, categories=["Fraud"])
    print(f"Result: {result2}")
    print(f"Expected: ['F1_HighAmount']")
    print(f"Success: {result2[0].get('id') == 'F1_HighAmount'}\n")

    # Test membership operators
    print("=== TEST 3: $in operator (VIP tiers) ===")
    data3 = {"user": {"tier": "Diamond", "status": "active"}}
    result3 = engine.evaluate_rules(data3, categories=["Membership"])
    print(f"Result: {result3}")
    print(f"Expected: ['M1_VIP_Tier']")
    print(f"Success: {result3[0].get('id') == 'M1_VIP_Tier'}\n")

    print("=== TEST 4: $not-in operator (Not blocked status) ===")
    data4 = {"user": {"tier": "Gold", "status": "active"}}
    result4 = engine.evaluate_rules(data4, categories=["Membership"])
    print(f"Result: {result4}")
    print(f"Expected: ['M2_Blocked_Status']")
    print(f"Success: {result4[0].get('id') == 'M2_Blocked_Status'}\n")

    print("=== TEST 5: $not-in operator (Blocked status - should not match) ===")
    data5 = {"user": {"tier": "Gold", "status": "banned"}}
    result5 = engine.evaluate_rules(data5, categories=["Membership"])
    print(f"Result: {result5}")
    print(f"Expected: [] (no match)")
    print(f"Success: {len(result5) == 0}\n")

    # Test string operators
    print("=== TEST 6: $contains operator (Case-sensitive) ===")
    data6 = {"description": "This is a premium account", "user": {"name": "John", "email": "john@test.com"}}
    result6 = engine.evaluate_rules(data6, categories=["StringOps"])
    print(f"Result: {result6}")
    print(f"Expected: ['S1_Contains_Premium']")
    print(f"Success: {any(r.get('id') == 'S1_Contains_Premium' for r in result6)}\n")

    print("=== TEST 7: $starts-with operator ===")
    data7 = {"description": "regular account", "user": {"name": "Dr. Smith", "email": "smith@test.com"}}
    result7 = engine.evaluate_rules(data7, categories=["StringOps"])
    print(f"Result: {result7}")
    print(f"Expected: ['S2_Starts_With_Dr']")
    print(f"Success: {any(r.get('id') == 'S2_Starts_With_Dr' for r in result7)}\n")

    print("=== TEST 8: $ends-with operator ===")
    data8 = {"description": "test", "user": {"name": "Alice", "email": "alice@company.com"}}
    result8 = engine.evaluate_rules(data8, categories=["StringOps"])
    print(f"Result: {result8}")
    print(f"Expected: ['S3_Ends_With_Domain']")
    print(f"Success: {any(r.get('id') == 'S3_Ends_With_Domain' for r in result8)}\n")

    print("=== TEST 9: All string operators together ===")
    data9 = {"description": "premium service", "user": {"name": "Dr. Jones", "email": "jones@company.com"}}
    result9 = engine.evaluate_rules(data9, categories=["StringOps"])
    print(f"Result: {result9}")
    print(f"Expected: ['S1_Contains_Premium', 'S2_Starts_With_Dr', 'S3_Ends_With_Domain']")
    print(f"Success: {len(result9) == 3}\n")

    # Test regex operator
    print("=== TEST 10: $regex operator (Valid email) ===")
    data10 = {"user": {"email": "test@example.com", "phone": "+1234567890"}}
    result10 = engine.evaluate_rules(data10, categories=["Validation"])
    print(f"Result: {result10}")
    print(f"Expected: ['V1_Email_Valid']")
    print(f"Success: {result10[0].get('id') == 'V1_Email_Valid'}\n")

    print("=== TEST 11: $regex operator (Invalid email, but valid phone) ===")
    data11 = {"user": {"email": "invalid-email", "phone": "+1234567890"}}
    result11 = engine.evaluate_rules(data11, categories=["Validation"])
    print(f"Result: {result11}")
    print(f"Expected: ['V2_Phone_Valid']")
    print(f"Success: {result11[0].get('id') == 'V2_Phone_Valid' if len(result11) > 0 else False}\n")

    # Test remaining comparison operators
    print("=== TEST 12: $not-equals operator ===")
    data12 = {"status": "active", "age": 30, "score": 75}
    result12 = engine.evaluate_rules(data12, categories=["Comparison"])
    print(f"Result: {result12}")
    print(f"Expected: ['C1_NotEqual']")
    print(f"Success: {any(r.get('id') == 'C1_NotEqual' for r in result12)}\n")

    print("=== TEST 13: $less-than operator (Minor) ===")
    data13 = {"status": "active", "age": 15, "score": 75}
    result13 = engine.evaluate_rules(data13, categories=["Comparison"])
    print(f"Result: {result13}")
    print(f"Expected: ['C1_NotEqual', 'C2_LessThan']")
    print(f"Success: {any(r.get('id') == 'C2_LessThan' for r in result13)}\n")

    print("=== TEST 14: $greater-than-or-equals operator (Senior) ===")
    data14 = {"status": "active", "age": 70, "score": 75}
    result14 = engine.evaluate_rules(data14, categories=["Comparison"])
    print(f"Result: {result14}")
    print(f"Expected: ['C1_NotEqual', 'C3_GreaterThanOrEquals']")
    print(f"Success: {any(r.get('id') == 'C3_GreaterThanOrEquals' for r in result14)}\n")

    print("=== TEST 15: $less-than-or-equals operator (Low score) ===")
    data15 = {"status": "active", "age": 25, "score": 45}
    result15 = engine.evaluate_rules(data15, categories=["Comparison"])
    print(f"Result: {result15}")
    print(f"Expected: ['C1_NotEqual', 'C4_LessThanOrEquals']")
    print(f"Success: {any(r.get('id') == 'C4_LessThanOrEquals' for r in result15)}\n")

    # Test multiple categories
    print("=== TEST 16: Multiple categories (Pricing + Fraud) ===")
    data16 = {"user": {"tier": "Platinum"}, "transaction": {"amount": 15000}}
    result16 = engine.evaluate_rules(data16, categories=["Pricing", "Fraud"])
    print(f"Result: {result16}")
    print(f"Expected: ['R1_Platinum', 'F1_HighAmount']")
    print(f"Success: {result16[0].get('id') == 'R1_Platinum' and result16[1].get('id') == 'F1_HighAmount'}\n")

    print("=" * 60)
    print("All tests completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()
