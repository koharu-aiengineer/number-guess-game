import csv
import os
import datetime
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from matplotlib.backends.backend_pdf import PdfPages

for font in ["Hiragino Sans", "Hiragino Maru Gothic Pro", "AppleGothic"]:
    if any(font in f.name for f in fm.fontManager.ttflist):
        matplotlib.rcParams["font.family"] = font
        break

matplotlib.rcParams["pdf.fonttype"] = 42
matplotlib.rcParams["ps.fonttype"] = 42


def load_csv(filepath):
    with open(filepath, encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    return rows


def detect_columns(headers):
    affiliation_keywords = {"所属", "部署", "学部", "学科", "グループ", "チーム", "department", "group"}
    score_keywords = {"スコア", "score", "点数", "得点", "点", "成績"}
    name_keywords = {"名前", "氏名", "name", "参加者"}

    affiliation_col = next((h for h in headers if h in affiliation_keywords), None)
    score_col = next((h for h in headers if h in score_keywords), None)
    name_col = next((h for h in headers if h in name_keywords), headers[0])

    return name_col, affiliation_col, score_col


def collect_scores(rows, score_col):
    scores = []
    for row in rows:
        try:
            scores.append(float(row[score_col]))
        except (ValueError, KeyError):
            pass
    return scores


def collect_by_affiliation(rows, affiliation_col, score_col):
    groups = {}
    for row in rows:
        affil = row.get(affiliation_col, "不明").strip() or "不明"
        groups.setdefault(affil, [])
        if score_col:
            try:
                groups[affil].append(float(row[score_col]))
            except (ValueError, KeyError):
                pass
        else:
            groups[affil].append(None)
    return groups


def make_pie_chart(groups):
    labels = list(groups.keys())
    sizes = [len(v) for v in groups.values()]

    fig, ax = plt.subplots(figsize=(8, 7))
    wedges, texts, autotexts = ax.pie(
        sizes,
        labels=labels,
        autopct="%1.1f%%",
        startangle=90,
        pctdistance=0.8,
        wedgeprops={"edgecolor": "white", "linewidth": 1.5},
    )
    for text in texts:
        text.set_fontsize(11)
    for autotext in autotexts:
        autotext.set_fontsize(10)
        autotext.set_fontweight("bold")

    ax.set_title("所属ごとの参加者数", fontsize=14, fontweight="bold", pad=20)
    total = sum(sizes)
    ax.legend(
        [f"{l}（{s}名）" for l, s in zip(labels, sizes)],
        title=f"合計: {total}名",
        loc="lower left",
        fontsize=9,
    )
    plt.tight_layout()
    return fig


def save_pie_chart(groups, output_path):
    fig = make_pie_chart(groups)
    fig.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  円グラフ保存: {output_path}")


def make_bar_chart(groups):
    labels = []
    avgs = []
    maxs = []
    mins = []

    for affil, scores in groups.items():
        valid = [s for s in scores if s is not None]
        if not valid:
            continue
        labels.append(affil)
        avgs.append(sum(valid) / len(valid))
        maxs.append(max(valid))
        mins.append(min(valid))

    if not labels:
        return None

    x = range(len(labels))
    width = 0.25

    fig, ax = plt.subplots(figsize=(max(8, len(labels) * 1.5), 6))
    ax.bar([i - width for i in x], avgs, width=width, label="平均スコア", color="#4C72B0", alpha=0.85)
    ax.bar([i for i in x], maxs, width=width, label="最高スコア", color="#55A868", alpha=0.85)
    ax.bar([i + width for i in x], mins, width=width, label="最低スコア", color="#C44E52", alpha=0.85)

    overall_avg = sum(avgs) / len(avgs)
    ax.axhline(overall_avg, color="navy", linestyle="--", linewidth=1.2, label=f"全体平均: {overall_avg:.1f}")

    for i, avg in enumerate(avgs):
        ax.text(i - width, avg + 0.5, f"{avg:.1f}", ha="center", va="bottom", fontsize=9)

    ax.set_xticks(list(x))
    ax.set_xticklabels(labels, fontsize=11)
    ax.set_xlabel("所属", fontsize=12)
    ax.set_ylabel("スコア", fontsize=12)
    ax.set_title("所属ごとの平均・最高・最低スコア", fontsize=14, fontweight="bold")
    ax.legend(fontsize=10)
    ax.grid(axis="y", alpha=0.3)
    ax.set_ylim(0, max(maxs) * 1.15)

    plt.tight_layout()
    return fig


def save_bar_chart(groups, output_path):
    fig = make_bar_chart(groups)
    if fig is None:
        print("  棒グラフ: スコアデータが見つからないためスキップします。")
        return
    fig.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  棒グラフ保存: {output_path}")


def make_histogram(scores):
    if not scores:
        return None

    import math
    bins = max(5, min(20, int(math.ceil(math.sqrt(len(scores))))))

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.hist(scores, bins=bins, color="#4C72B0", edgecolor="white", linewidth=0.8, alpha=0.85)

    mean = sum(scores) / len(scores)
    ax.axvline(mean, color="red", linestyle="--", linewidth=1.5, label=f"平均: {mean:.1f}")

    sorted_scores = sorted(scores)
    median = sorted_scores[len(sorted_scores) // 2]
    ax.axvline(median, color="orange", linestyle=":", linewidth=1.5, label=f"中央値: {median:.1f}")

    ax.set_xlabel("スコア", fontsize=12)
    ax.set_ylabel("人数", fontsize=12)
    ax.set_title("スコア分布（ヒストグラム）", fontsize=14, fontweight="bold")
    ax.legend(fontsize=10)
    ax.grid(axis="y", alpha=0.3)

    plt.tight_layout()
    return fig


def save_histogram(scores, output_path):
    fig = make_histogram(scores)
    if fig is None:
        print("  ヒストグラム: スコアデータが見つからないためスキップします。")
        return
    fig.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  ヒストグラム保存: {output_path}")


def build_analysis_lines(groups, scores):
    lines = []

    if groups:
        total = sum(len(v) for v in groups.values())
        sorted_groups = sorted(groups.items(), key=lambda x: len(x[1]), reverse=True)
        top_affil, top_members = sorted_groups[0]
        bot_affil, bot_members = sorted_groups[-1]
        lines.append("【所属構成】")
        lines.append(f"  参加者は {len(groups)} 部門・合計 {total} 名")
        lines.append(f"  最多: 「{top_affil}」({len(top_members)}名 / {len(top_members)/total*100:.1f}%)")
        if len(sorted_groups) >= 2:
            lines.append(f"  最少: 「{bot_affil}」({len(bot_members)}名 / {len(bot_members)/total*100:.1f}%)")

    affil_stats = {}
    for affil, sc_list in (groups or {}).items():
        valid = [s for s in sc_list if s is not None]
        if valid:
            affil_stats[affil] = {
                "avg": sum(valid) / len(valid),
                "max": max(valid),
                "min": min(valid),
                "spread": max(valid) - min(valid),
            }

    if affil_stats:
        overall_avg = sum(s["avg"] for s in affil_stats.values()) / len(affil_stats)
        best = max(affil_stats, key=lambda k: affil_stats[k]["avg"])
        worst = min(affil_stats, key=lambda k: affil_stats[k]["avg"])
        most_spread = max(affil_stats, key=lambda k: affil_stats[k]["spread"])
        above = [k for k, v in affil_stats.items() if v["avg"] >= overall_avg]
        below = [k for k, v in affil_stats.items() if v["avg"] < overall_avg]
        lines.append("")
        lines.append("【所属別スコア比較】")
        lines.append(f"  全体平均: {overall_avg:.1f} 点")
        lines.append(f"  最高平均: 「{best}」({affil_stats[best]['avg']:.1f} 点)")
        lines.append(f"  最低平均: 「{worst}」({affil_stats[worst]['avg']:.1f} 点)  ← フォローアップ候補")
        lines.append(f"  平均以上の部門: {' / '.join(above)}")
        lines.append(f"  平均未満の部門: {' / '.join(below)}")
        lines.append(f"  ばらつき最大: 「{most_spread}」(最高-最低 = {affil_stats[most_spread]['spread']:.0f} 点差)")

    if scores:
        mean = sum(scores) / len(scores)
        sorted_sc = sorted(scores)
        median = sorted_sc[len(sorted_sc) // 2]
        low_threshold = mean - 15
        low_count = sum(1 for s in scores if s < low_threshold)
        high_count = sum(1 for s in scores if s >= 90)
        lines.append("")
        lines.append("【スコア分布】")
        lines.append(f"  平均 {mean:.1f} 点 / 中央値 {median:.1f} 点 / 最小 {min(scores):.0f} 点 / 最大 {max(scores):.0f} 点")
        if abs(mean - median) <= 3:
            lines.append("  → 平均と中央値が近く、分布に大きな偏りはありません")
        elif mean < median:
            lines.append("  → 平均 < 中央値のため、低得点者が全体を引き下げている可能性があります")
        else:
            lines.append("  → 平均 > 中央値のため、高得点者が平均を押し上げている可能性があります")
        if high_count:
            lines.append(f"  90点以上の高得点者: {high_count} 名")
        if low_count:
            lines.append(f"  {low_threshold:.0f}点未満の低得点者: {low_count} 名  ← 個別サポートを検討")

    return lines


def make_title_page(filename, groups, scores):
    total = sum(len(v) for v in groups.values()) if groups else (len(scores) if scores else 0)
    dept_count = len(groups) if groups else "-"
    overall_avg = "-"
    if scores:
        overall_avg = f"{sum(scores)/len(scores):.1f} 点"
    date_str = datetime.date.today().strftime("%Y年%m月%d日")

    fig = plt.figure(figsize=(8.27, 11.69))
    fig.patch.set_facecolor("#f7f9fc")

    fig.text(0.5, 0.82, "スコア分析レポート", ha="center", fontsize=28, fontweight="bold", color="#1a1a2e")
    fig.text(0.5, 0.76, date_str, ha="center", fontsize=14, color="#555")
    fig.text(0.5, 0.72, f"データソース: {os.path.basename(filename)}", ha="center", fontsize=11, color="#777")

    fig.add_artist(plt.matplotlib.patches.FancyBboxPatch(
        (0.1, 0.52), 0.8, 0.14,
        boxstyle="round,pad=0.02", linewidth=0,
        facecolor="#e8eef7", transform=fig.transFigure
    ))
    fig.text(0.3, 0.62, f"参加者数\n{total} 名", ha="center", va="center", fontsize=16,
             fontweight="bold", color="#1a1a2e")
    fig.text(0.5, 0.62, f"部門数\n{dept_count} 部門", ha="center", va="center", fontsize=16,
             fontweight="bold", color="#1a1a2e")
    fig.text(0.7, 0.62, f"全体平均\n{overall_avg}", ha="center", va="center", fontsize=16,
             fontweight="bold", color="#1a1a2e")

    fig.text(0.1, 0.47, "本レポートの構成", fontsize=13, fontweight="bold", color="#1a1a2e")
    contents = [
        "1. 所属ごとの参加者数（円グラフ）",
        "2. 所属ごとの平均・最高・最低スコア（棒グラフ）",
        "3. 全参加者のスコア分布（ヒストグラム）",
        "4. データ考察",
    ]
    for i, line in enumerate(contents):
        fig.text(0.12, 0.42 - i * 0.055, line, fontsize=11, color="#333")

    return fig


def make_analysis_page(groups, scores):
    lines = build_analysis_lines(groups, scores)

    fig = plt.figure(figsize=(8.27, 11.69))
    fig.patch.set_facecolor("#f7f9fc")
    fig.text(0.5, 0.93, "データ考察", ha="center", fontsize=20, fontweight="bold", color="#1a1a2e")

    y = 0.87
    for line in lines:
        is_header = line.startswith("【")
        fontsize = 12 if is_header else 10
        color = "#1a1a2e" if is_header else "#333"
        bold = "bold" if is_header else "normal"
        if is_header and y < 0.87:
            y -= 0.01
        fig.text(0.08, y, line, fontsize=fontsize, fontweight=bold, color=color)
        y -= 0.045 if is_header else 0.038
        if y < 0.05:
            break

    return fig


def save_pdf_report(filepath, groups, scores, output_path):
    print(f"  PDFレポート生成中...")
    with PdfPages(output_path) as pdf:
        fig = make_title_page(filepath, groups, scores)
        pdf.savefig(fig, bbox_inches="tight")
        plt.close(fig)

        if groups:
            fig = make_pie_chart(groups)
            pdf.savefig(fig, bbox_inches="tight")
            plt.close(fig)

            if any(s is not None for sc in groups.values() for s in sc):
                fig = make_bar_chart(groups)
                if fig:
                    pdf.savefig(fig, bbox_inches="tight")
                    plt.close(fig)

        if scores:
            fig = make_histogram(scores)
            if fig:
                pdf.savefig(fig, bbox_inches="tight")
                plt.close(fig)

        fig = make_analysis_page(groups, scores)
        pdf.savefig(fig, bbox_inches="tight")
        plt.close(fig)

    print(f"  PDFレポート保存: {output_path}")


def print_analysis(groups, scores):
    lines = build_analysis_lines(groups, scores)
    print()
    print("=" * 60)
    print("  データ考察")
    print("=" * 60)
    for line in lines:
        print(f"  {line}" if line else "")
    print()
    print("=" * 60)
    print()


def main():
    print("=== グラフ生成プログラム ===")
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
    name_col, affiliation_col, score_col = detect_columns(headers)

    print(f"\n検出された列:")
    print(f"  名前列    : {name_col}")
    print(f"  所属列    : {affiliation_col or '未検出'}")
    print(f"  スコア列  : {score_col or '未検出'}")

    if not affiliation_col:
        print("\n警告: 所属列が自動検出できませんでした。")
        user_input = input(f"所属列の列名を入力してください（列候補: {', '.join(headers)}）: ").strip()
        affiliation_col = user_input if user_input in headers else None

    if not score_col:
        print("\n警告: スコア列が自動検出できませんでした。")
        user_input = input(f"スコア列の列名を入力してください（列候補: {', '.join(headers)}）: ").strip()
        score_col = user_input if user_input in headers else None

    output_dir = os.path.dirname(os.path.abspath(filepath))
    print(f"\nグラフを生成・保存しています（保存先: {output_dir}）\n")

    if affiliation_col:
        groups = collect_by_affiliation(rows, affiliation_col, score_col)
        save_pie_chart(groups, os.path.join(output_dir, "pie_chart.png"))
        if score_col:
            save_bar_chart(groups, os.path.join(output_dir, "bar_chart.png"))
    else:
        print("  所属列がないため、円グラフと棒グラフをスキップします。")

    if score_col:
        scores = collect_scores(rows, score_col)
        save_histogram(scores, os.path.join(output_dir, "histogram.png"))
    else:
        scores = []
        print("  スコア列がないため、ヒストグラムをスキップします。")

    print_analysis(groups if affiliation_col else None, scores)

    pdf_path = os.path.join(output_dir, "score_report.pdf")
    save_pdf_report(filepath, groups if affiliation_col else None, scores, pdf_path)

    print("完了しました。")


if __name__ == "__main__":
    main()
