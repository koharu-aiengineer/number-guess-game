def calculate(a, b, op):
    if op == '+':
        return a + b
    elif op == '-':
        return a - b
    elif op == '*':
        return a * b
    elif op == '/':
        if b == 0:
            return None
        return a / b


def show_history(history):
    if not history:
        print("履歴はありません。")
        return
    print("=== 計算履歴 ===")
    for i, entry in enumerate(history, 1):
        print(f"  {i}. {entry}")
    print()


def main():
    print("=== 簡易計算機 ===")
    history = []

    while True:
        try:
            a = float(input("1つ目の数値を入力: "))
            op = input("演算子を入力 (+ - * /): ").strip()
            b = float(input("2つ目の数値を入力: "))
        except ValueError:
            print("エラー: 有効な数値を入力してください。")
        else:
            if op not in ('+', '-', '*', '/'):
                print(f"エラー: 無効な演算子です → '{op}'")
            else:
                result = calculate(a, b, op)
                if result is None:
                    print("エラー: 0 で割ることはできません。")
                else:
                    print(f"結果: {a} {op} {b} = {result}")
                    history.append(f"{a} {op} {b} = {result}")

        print("\n次の操作を選んでください:")
        print("  y: もう一度計算する")
        print("  h: 履歴を表示する")
        print("  n: 終了する")
        choice = input("選択 (y / h / n): ").strip().lower()

        if choice == 'y':
            print()
        elif choice == 'h':
            print()
            show_history(history)
        else:
            print("終了します。")
            break


if __name__ == "__main__":
    main()
