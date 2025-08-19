#!/usr/bin/env python3
import argparse, json, os, random, sys, time
from datetime import datetime
try:
    import yaml  # pip install pyyaml
except ImportError:
    print("Please: pip install pyyaml", file=sys.stderr)
    sys.exit(1)

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich.text import Text
except ImportError:
    print("Please: pip install rich", file=sys.stderr)
    sys.exit(1)

STATE_PATH = os.path.expanduser("~/.sdi_cards_state.json")
console = Console()

def load_cards(path, tags=None):
    all_cards = []
    # Store deck info temporarily
    deck_info = {}

    if os.path.isdir(path):
        for root, _, files in os.walk(path):
            for file in files:
                if file.endswith((".yaml", ".yml")):
                    filepath = os.path.join(root, file)
                    with open(filepath, "r", encoding="utf-8") as f:
                        data = yaml.safe_load(f)
                        if data:
                            # Extract deck info from meta
                            if "meta" in data and "deck" in data["meta"]:
                                deck_data = data["meta"]["deck"]
                                if isinstance(deck_data, dict):
                                    deck_info["ja"] = deck_data.get("ja", "Unknown Deck (Ja)")
                                    deck_info["en"] = deck_data.get("en", "Unknown Deck (En)")
                                else: # Fallback for old string format
                                    deck_info["ja"] = deck_data
                                    deck_info["en"] = deck_data
                            else:
                                deck_info["ja"] = "Unknown Deck (Ja)"
                                deck_info["en"] = "Unknown Deck (En)"

                            if "cards" in data:
                                for card in data["cards"]:
                                    # Handle new term structure
                                    if isinstance(card.get("term"), dict):
                                        card["_term_ja"] = card["term"].get("ja", "")
                                        card["_term_en"] = card["term"].get("en", "")
                                    else: # Fallback for old string format
                                        card["_term_ja"] = card.get("term", "")
                                        card["_term_en"] = card.get("term", "") # Use same for en if not specified

                                    card["_deck_name_ja"] = deck_info["ja"]
                                    card["_deck_name_en"] = deck_info["en"]
                                    all_cards.append(card)
    elif os.path.isfile(path):
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
            if data:
                # Extract deck info from meta
                if "meta" in data and "deck" in data["meta"]:
                    deck_data = data["meta"]["deck"]
                    if isinstance(deck_data, dict):
                        deck_info["ja"] = deck_data.get("ja", "Unknown Deck (Ja)")
                        deck_info["en"] = deck_data.get("en", "Unknown Deck (En)")
                    else: # Fallback for old string format
                        deck_info["ja"] = deck_data
                        deck_info["en"] = deck_data
                else:
                    deck_info["ja"] = "Unknown Deck (Ja)"
                    deck_info["en"] = "Unknown Deck (En)"

                if "cards" in data:
                    for card in data["cards"]:
                        # Handle new term structure
                        if isinstance(card.get("term"), dict):
                            card["_term_ja"] = card["term"].get("ja", "")
                            card["_term_en"] = card["term"].get("en", "")
                        else: # Fallback for old string format
                            card["_term_ja"] = card.get("term", "")
                            card["_term_en"] = card.get("term", "") # Use same for en if not specified

                        card["_deck_name_ja"] = deck_info["ja"]
                        card["_deck_name_en"] = deck_info["en"]
                        all_cards.append(card)
    else:
        # Handle invalid path (neither file nor directory)
        return []

    cards = all_cards
    if tags:
        tagset = set(tags)
        cards = [c for c in cards if tagset & set(c.get("tags", []))]
    # 進捗付与
    state = load_state()
    for c in cards:
        cid = c.get("id", c.get("term"))
        s = state.get(cid, {"box": 1, "streak": 0, "last": None, "seen": 0, "ok": 0})
        c["_state"] = s
    return cards

def load_state():
    if os.path.exists(STATE_PATH):
        try:
            with open(STATE_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_state(cards):
    state = load_state()
    for c in cards:
        cid = c.get("id", c.get("term"))
        s = c.get("_state", {})
        state[cid] = s
    os.makedirs(os.path.dirname(STATE_PATH), exist_ok=True)
    with open(STATE_PATH, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)

def due_score(s):
    """Leitner風の出題優先度。boxが小さいほど優先、未学習も優先。"""
    box = s.get("box", 1)
    last = s.get("last")
    # 経過時間で軽く重み付け（雑だけど実用十分）
    elapsed = 0
    if last:
        try:
            elapsed = max(0, time.time() - float(last))
        except:
            elapsed = 0
    return (box, -elapsed)  # box昇順、長く出してない順

def quiz(cards, count=20, reverse=False, verbose=False):
    if reverse:
        original_card_count = len(cards)
        cards = [c for c in cards if 'recall_question' in c]
        if not cards:
            console.print("[bold yellow]リバースクイズには 'recall_question' キーを持つカードが必要です。対象のカードが見つかりませんでした。[/bold yellow]")
            return
        console.print(f"[bold dim]リバースクイズ用に 'recall_question' を持つカード {len(cards)}/{original_card_count} 枚を対象とします。[/bold dim]")

    # 出題順：弱いカード優先（box小）
    cards_sorted = sorted(cards, key=lambda c: due_score(c["_state"]))
    pool = cards_sorted[:max(count, 1)]
    random.shuffle(pool)
    correct = 0
    total = 0

    try:
        for c in pool:
            cid = c.get("id", c.get("_term_ja", c.get("term", "?"))) # Use _term_ja if id is missing, fallback to original term
            
            # Construct the term string with both Japanese and English
            term_ja = c.get("_term_ja", "").strip()
            term_en = c.get("_term_en", "").strip()
            
            if term_ja and term_en and term_ja != term_en:
                display_term = f"{term_ja} ({term_en})"
            elif term_ja:
                display_term = term_ja
            elif term_en:
                display_term = term_en
            else:
                display_term = c.get("term", "Unknown Term").strip() # Fallback to original term if new fields are empty

            definition = c["definition"].strip()
            
            if reverse:
                prompt = c['recall_question'].strip()
                answer = display_term
            else:
                prompt = display_term
                answer = definition
            
            console.print()
            console.print(Panel(prompt, title=f"[bold cyan]Q: {cid} ({c['_deck_name_ja']} / {c['_deck_name_en']})[/bold cyan]", border_style="cyan"))
            input("↩︎ Enter で解答を表示...")
            
            answer_text = Text(f"👉 {answer}", style="bold green")
            console.print(answer_text)

            if verbose and c.get("explanation"):
                console.print(Panel(c['explanation'], title="[bold yellow]Explanation[/bold yellow]", border_style="yellow", expand=False))
            notes = c.get("notes")
            if notes:
                console.print(f"   [dim]💬 Notes:[/dim]")
                for note in notes:
                    console.print(f"      [dim]- {note}[/dim]")
            urls = c.get("url")
            if urls:
                if not isinstance(urls, list):
                    urls = [urls]
                console.print(f"   [dim]🔗 URLs:[/dim]")
                for url in urls:
                    console.print(f"      [dim]- {url}[/dim]")

            yn = input("✔ 正解？ (y/n): ").strip().lower()
            s = c["_state"]
            s["seen"] = s.get("seen", 0) + 1
            s["last"] = time.time()

            if yn == "y":
                correct += 1
                s["ok"] = s.get("ok", 0) + 1
                s["streak"] = s.get("streak", 0) + 1
                s["box"] = min(5, s.get("box", 1) + 1)
                console.print("[bold green]✔ Correct![/bold green]")
            else:
                s["streak"] = 0
                s["box"] = 1
                console.print("[bold red]✖ Incorrect.[/bold red]")

            total += 1
    except KeyboardInterrupt:
        console.print("\n[bold yellow]クイズを中断しました。お疲れ様でした！[/bold yellow]")
        save_state(cards)
        sys.exit(0)

    console.print()
    # totalが0の場合のゼロ除算を避ける
    if total > 0:
        score_text = f"Score: {correct}/{total} ({(100*correct/total):.1f}%)"
        console.print(Panel(score_text, title="[bold magenta]Quiz Result[/bold magenta]", border_style="magenta"))
    
    save_state(cards)

def list_cards(cards, verbose=False):
    for c in cards:
        tags = ", ".join(c.get("tags", []))
        text = Text()
        text.append(f"- {c.get('id','?')}:", style="bold cyan")
        text.append(f" {c['term']}  ")
        text.append(f"[{tags}]", style="dim")
        console.print(text)
        if verbose and c.get("explanation"):
            console.print(f"    [dim]{c['explanation']}[/dim]")


def show_stats(cards):
    state = load_state()
    if not state:
        console.print("[yellow]No stats yet. Start a quiz first.[/yellow]")
        return

    total_cards = len(cards)
    reviewed_cards = [c for c in cards if c["_state"]["seen"] > 0]
    total_seen = sum(c["_state"]["seen"] for c in reviewed_cards)
    total_ok = sum(c["_state"]["ok"] for c in reviewed_cards)
    overall_accuracy = (total_ok / total_seen * 100) if total_seen > 0 else 0

    # Overall Stats Panel
    # Overall Stats Panel
    accuracy_style = "green" if overall_accuracy > 80 else "yellow"
    stats_summary = Text()
    stats_summary.append("Total cards: ")
    stats_summary.append(str(total_cards), style="bold")
    stats_summary.append("\nReviewed cards: ")
    stats_summary.append(str(len(reviewed_cards)), style="bold")
    stats_summary.append("\nTotal reviews: ")
    stats_summary.append(str(total_seen), style="bold")
    stats_summary.append("\nOverall accuracy: ")
    stats_summary.append(f"{overall_accuracy:.1f}%", style=f"bold {accuracy_style}")
    console.print(Panel(stats_summary, title="[bold magenta]Overall Stats[/bold magenta]", border_style="magenta"))

    # Per-Card Stats Table
    table = Table(title="[bold cyan]Per-Card Stats[/bold cyan]")
    table.add_column("ID", style="cyan", no_wrap=True)
    table.add_column("Box", style="magenta")
    table.add_column("Streak", style="green")
    table.add_column("Seen", style="blue")
    table.add_column("OK", style="green")
    table.add_column("Accuracy", style="yellow")
    table.add_column("Last Review", style="dim")

    cards_sorted = sorted(reviewed_cards, key=lambda c: due_score(c["_state"]))
    for c in cards_sorted:
        s = c["_state"]
        cid = c.get("id", c["term"])
        accuracy = (s['ok'] / s['seen'] * 100) if s['seen'] > 0 else 0
        accuracy_str = f"{accuracy:.1f}%"
        last_review_str = datetime.fromtimestamp(s['last']).strftime('%Y-%m-%d %H:%M') if s.get('last') else 'Never'
        table.add_row(cid, str(s['box']), str(s['streak']), str(s['seen']), str(s['ok']), accuracy_str, last_review_str)
    console.print(table)

    # Per-Tag Stats Table
    tag_table = Table(title="[bold cyan]Per-Tag Stats[/bold cyan]")
    tag_table.add_column("Tag", style="cyan", no_wrap=True)
    tag_table.add_column("Cards", style="magenta")
    tag_table.add_column("Reviews", style="blue")
    tag_table.add_column("Accuracy", style="yellow")

    tag_stats = {}
    for c in cards:
        for tag in c.get("tags", []):
            if tag not in tag_stats:
                tag_stats[tag] = {"cards": 0, "seen": 0, "ok": 0}
            tag_stats[tag]["cards"] += 1
            s = c["_state"]
            if s["seen"] > 0:
                tag_stats[tag]["seen"] += s["seen"]
                tag_stats[tag]["ok"] += s["ok"]

    for tag, stats in sorted(tag_stats.items()):
        accuracy = (stats['ok'] / stats['seen'] * 100) if stats['seen'] > 0 else 0
        tag_table.add_row(tag, str(stats['cards']), str(stats['seen']), f"{accuracy:.1f}%")
    console.print(tag_table)

def main():
    ap = argparse.ArgumentParser(description="SDI Flashcards (YAML-driven)")
    ap.add_argument("-f", "--file", default="cards/", help="YAML file or directory path")
    ap.add_argument("-t", "--tags", nargs="*", help="Filter by tags (space-separated)")
    ap.add_argument("-n", "--count", type=int, default=15, help="Number of questions")
    ap.add_argument("-r", "--reverse", action="store_true", help="Reverse (definition -> term)")
    ap.add_argument("-v", "--verbose", action="store_true", help="Show long description")
    ap.add_argument("--list", action="store_true", help="List cards and exit")
    ap.add_argument("--stats", action="store_true", help="Show learning statistics")
    args = ap.parse_args()

    cards = load_cards(args.file, tags=args.tags)
    if not cards:
        console.print("[bold red]No cards found. Check YAML or tag filter.[/bold red]")
        sys.exit(1)

    if args.list:
        list_cards(cards, verbose=args.verbose)
    elif args.stats:
        show_stats(cards)
    else:
        quiz(cards, count=args.count, reverse=args.reverse, verbose=args.verbose)

if __name__ == "__main__":
    main()
