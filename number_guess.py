import random


def play_game():
    secret = random.randint(1, 100)
    attempts = 0

    print("=== 数当てゲーム ===")
    print("1〜100の整数を当ててください！")
    print()

    while True:
        try:
            guess = int(input("数字を入力してください: "))
        except ValueError:
            print("整数を入力してください。\n")
            continue

        if guess < 1 or guess > 100:
            print("1〜100の範囲で入力してください。\n")
            continue

        attempts += 1

        if guess < secret:
            print("もっと大きい数字です。\n")
        elif guess > secret:
            print("もっと小さい数字です。\n")
        else:
            print(f"正解！ {secret} です！")
            print(f"試行回数: {attempts} 回")
            break


def main():
    while True:
        play_game()
        print()
        again = input("もう一度プレイしますか？ (y/n): ").strip().lower()
        if again != "y":
            print("ゲームを終了します。")
            break
        print()


if __name__ == "__main__":
    main()
