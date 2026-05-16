import csv
import os
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

# macOSの日本語フォントを設定
for font in ["Hiragino Sans", "Hiragino Maru Gothic Pro", "AppleGothic"]:
    if any(font in f.name for f in fm.fontManager.ttflist):
        matplotlib.rcParams["font.family"] = font
        break


def load_csv(filepath):
    with open(filepath, encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    return rows


def is_long_format(headers):
    score_keywords = {"スコア", "score", "点数", "得点"}
    return any(h in score_keywords for h in headers)


def analyze_long(rows, name_col, score_col, subject_col=None):
    by_name = {}
    by_subject = {}
    for row in rows:
        name = row[name_col]
        try:
            score = float(row[score_col])
        except ValueError:
            continue
        by_name.setdefault(name, []).append(score)
        if subject_col and row.get(subject_col):
            subject = row[subject_col]
            by_subject.setdefault(subject, []).append(score)

    results = []
    for name, scores in by_name.items():
        results.append({
            "name": name,
            "avg": sum(scores) / len(scores),
            "max": max(scores),
            "min": min(scores),
            "count": len(scores),
        })

    subject_results = []
    for subject, scores in by_subject.items():
        subject_results.append({
            "name": subject,
            "avg": sum(scores) / len(scores),
            "max": max(scores),
            "min": min(scores),
            "count": len(scores),
        })

    return results, subject_results


def analyze_wide(rows, name_col):
    results = []
    for row in rows:
        name = row[name_col]
        scores = []
        for key, val in row.items():
            if key == name_col:
                continue
            try:
                scores.append(float(val))
            except ValueError:
                pass
        if not scores:
            continue
        results.append({
            "name": name,
            "avg": sum(scores) / len(scores),
            "max": max(scores),
            "min": min(scores),
            "count": len(scores),
        })
    return results


def display_table(title, rows, name_label="名前"):
    print()
    print("=" * 60)
    print(f"  {title}")
    print("=" * 60)
    print(f"  {name_label:<12} {'平均':>8} {'最高点':>8} {'最低点':>8} {'件数':>6}")
    print("-" * 60)
    for r in sorted(rows, key=lambda r: r["avg"], reverse=True):
        print(f"  {r['name']:<12} {r['avg']:>7.1f} {r['max']:>8.0f} {r['min']:>8.0f} {r['count']:>5}件")
    print("=" * 60)


def display(results, subject_results=None):
    display_table("参加者別 スコア集計", results, "名前")

    avgs = [r["avg"] for r in results]
    top = max(results, key=lambda r: r["avg"])
    print(f"\n  全体平均: {sum(avgs) / len(avgs):.1f} 点")
    print(f"  最優秀者: {top['name']} (平均 {top['avg']:.1f} 点)")

    if subject_results:
        display_table("科目別 スコア集計", subject_results, "科目")
        hardest = min(subject_results, key=lambda r: r["avg"])
        easiest = max(subject_results, key=lambda r: r["avg"])
        print(f"\n  最高平均の科目: {easiest['name']} ({easiest['avg']:.1f} 点)")
        print(f"  最低平均の科目: {hardest['name']} ({hardest['avg']:.1f} 点)")

    print()


def plot_bar(ax, items, title, xlabel, color):
    items_sorted = sorted(items, key=lambda r: r["avg"])
    names = [r["name"] for r in items_sorted]
    avgs = [r["avg"] for r in items_sorted]
    maxs = [r["max"] for r in items_sorted]
    mins = [r["min"] for r in items_sorted]

    y = range(len(names))
    bars = ax.barh(y, avgs, color=color, alpha=0.8, label="平均")
    ax.barh(y, maxs, color=color, alpha=0.3, label="最高点")
    ax.barh(y, mins, color="gray", alpha=0.3, label="最低点")

    for i, (bar, avg) in enumerate(zip(bars, avgs)):
        ax.text(avg + 0.5, i, f"{avg:.1f}", va="center", fontsize=9)

    ax.set_yticks(y)
    ax.set_yticklabels(names)
    ax.set_xlabel(xlabel)
    ax.set_title(title, fontsize=13, fontweight="bold")
    ax.set_xlim(0, 110)
    ax.axvline(x=sum(avgs) / len(avgs), color="red", linestyle="--", linewidth=1, label="平均ライン")
    ax.legend(loc="lower right", fontsize=8)
    ax.grid(axis="x", alpha=0.3)


def show_graph(results, subject_results=None):
    n_plots = 2 if subject_results else 1
    fig, axes = plt.subplots(1, n_plots, figsize=(7 * n_plots, max(4, len(results) * 0.7 + 2)))
    fig.suptitle("スコア分析レポート", fontsize=15, fontweight="bold")

    ax_list = [axes] if n_plots == 1 else axes
    plot_bar(ax_list[0], results, "参加者別 平均スコア", "スコア", "#4C72B0")

    if subject_results:
        plot_bar(ax_list[1], subject_results, "科目別 平均スコア", "スコア", "#55A868")

    plt.tight_layout()
    plt.show()


def main():
    print("=== スコア分析プログラム ===")
    filepath = input("\nCSVファイルのパスを入力してください: ").strip().strip("'\"")

    if not os.path.exists(filepath):
        print(f"エラー: ファイルが見つかりません → {filepath}")
        return

    try:
        rows = load_csv(filepath)
    except Exception as e:
        print(f"エラー: ファイルの読み込みに失敗しました → {e}")
        return

    if not rows:
        print("エラー: データが空です。")
        return

    headers = list(rows[0].keys())
    name_col = headers[0]

    if is_long_format(headers):
        score_keywords = {"スコア", "score", "点数", "得点"}
        subject_keywords = {"科目", "subject", "教科"}
        score_col = next(h for h in headers if h in score_keywords)
        subject_col = next((h for h in headers if h in subject_keywords), None)
        print(f"\n形式: 縦長形式（名前列: {name_col} / スコア列: {score_col}）")
        results, subject_results = analyze_long(rows, name_col, score_col, subject_col)
    else:
        score_cols = [h for h in headers if h != name_col]
        print(f"\n形式: 横広形式（名前列: {name_col} / 科目: {', '.join(score_cols)}）")
        results = analyze_wide(rows, name_col)
        subject_results = None

    if not results:
        print("エラー: 数値データが見つかりませんでした。")
        return

    display(results, subject_results)
    show_graph(results, subject_results)


if __name__ == "__main__":
    main()
