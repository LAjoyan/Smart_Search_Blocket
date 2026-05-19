import platform
import subprocess
import sys

from rich.console import Console
from rich.panel import Panel
from rich.text import Text

try:
    from plyer import notification

    PLYER_AVAILABLE = True
except Exception:
    PLYER_AVAILABLE = False

try:
    import streamlit as st
    from streamlit.runtime.scriptrunner import get_script_run_ctx

    STREAMLIT_AVAILABLE = True
except Exception:
    STREAMLIT_AVAILABLE = False

console = Console()


def _in_streamlit() -> bool:
    """True only when this function is called from inside a running Streamlit app."""
    if not STREAMLIT_AVAILABLE:
        return False
    try:
        return get_script_run_ctx() is not None
    except Exception:
        return False


def _score_color(score: int) -> str:
    if score >= 8:
        return "green"
    if score >= 5:
        return "yellow"
    return "red"


def _score_emoji(score: int) -> str:
    if score >= 8:
        return "✅"
    if score >= 5:
        return "⚠️"
    return "🚨"


def _print_terminal(ad: dict, score: int, reasons: list[str]) -> None:
    title = ad.get("heading", "(no title)")
    price_data = ad.get("price") or {}
    price = price_data.get("amount") if isinstance(price_data, dict) else price_data
    location = ad.get("location") or "Unknown"
    url = ad.get("canonical_url", "")
    color = _score_color(score)

    body = Text()
    body.append("💰  Price:    ", style="bold")
    body.append(f"{price} SEK\n" if price else "—\n")
    body.append("📍  Location: ", style="bold")
    body.append(f"{location}\n")
    body.append("⭐  Trust:    ", style="bold")
    body.append(f"{score}/10\n", style=f"bold {color}")
    body.append("🔗  ", style="bold")
    body.append(f"{url}\n\n", style="dim underline")
    body.append("Why it matches:\n", style="bold")
    for r in reasons:
        body.append(f"  • {r}\n")

    console.print(
        Panel(body, title=f"🆕 New ad: {title}", border_style=color, padding=(1, 2))
    )


def _show_streamlit(ad: dict, score: int, reasons: list[str]) -> None:
    title = ad.get("heading", "(no title)")
    price_data = ad.get("price") or {}
    price = price_data.get("amount") if isinstance(price_data, dict) else price_data
    location = ad.get("location") or "Unknown"
    url = ad.get("canonical_url", "")
    emoji = _score_emoji(score)

    st.toast(f"{emoji} New ad ({score}/10) — {title[:60]}", icon="🆕")

    box = st.success if score >= 8 else (st.warning if score >= 5 else st.error)
    body = (
        f"**{title}**  \n"
        f"💰 {price} SEK · 📍 {location} · ⭐ {score}/10  \n"
        f"[Open on Blocket]({url})  \n\n"
        f"**Why it matches:**  \n" + "\n".join(f"- {r}" for r in reasons)
    )
    box(body)


def _popup_native(ad: dict, score: int) -> None:
    title = ad.get("heading", "(no title)")
    price_data = ad.get("price") or {}
    price = price_data.get("amount") if isinstance(price_data, dict) else price_data
    location = ad.get("location") or "Unknown"
    popup_title = f"{_score_emoji(score)} New ad · {score}/10"
    price_str = f"{price} SEK · " if price else ""
    popup_msg = f"{title}\n{price_str}{location}"

    if platform.system() == "Darwin":
        # macOS: osascript is built-in. AppleScript uses double-quoted strings;
        # escape any embedded double quotes/backslashes in our text.
        def _esc(s: str) -> str:
            return s.replace("\\", "\\\\").replace('"', '\\"')

        script = (
            f'display notification "{_esc(popup_msg)}" with title "{_esc(popup_title)}"'
        )
        try:
            subprocess.run(["osascript", "-e", script], check=False, timeout=3)
            return
        except Exception:
            pass

    if PLYER_AVAILABLE:
        try:
            notification.notify(title=popup_title, message=popup_msg, timeout=5)
        except Exception:
            pass


def notify_new_ad(ad: dict, score: int, reasons: list[str]) -> None:
    """
    Notify the user about a new matching ad.

    Surfaces (in order):
      1. Streamlit toast + colored card  — if called from inside a Streamlit app
      2. Rich terminal panel             — otherwise
      3. Native OS popup (plyer)         — always, if plyer is installed
      4. Terminal bell                   — always
    """
    if _in_streamlit():
        _show_streamlit(ad, score, reasons)
    else:
        _print_terminal(ad, score, reasons)

    _popup_native(ad, score)

    sys.stdout.write("\a")
    sys.stdout.flush()


if __name__ == "__main__":
    trusted = {
        "heading": "iPhone 13 Pro Max 512GB Sierra Blue – Som Ny",
        "price": {"amount": 4500},
        "location": "Stockholm",
        "canonical_url": "https://www.blocket.se/recommerce/forsale/item/12345678",
    }
    notify_new_ad(
        trusted,
        score=9,
        reasons=["Reasonable price", "Multiple images provided", "Location: Stockholm"],
    )

    suspicious = {
        "heading": "Apple iPhone 13 mobil 128 GB vit",
        "price": {"amount": 1200},
        "location": "Ösmo",
        "canonical_url": "https://www.blocket.se/recommerce/forsale/item/23297392",
    }
    notify_new_ad(
        suspicious,
        score=4,
        reasons=["Unreasonably low price (1200 SEK vs avg 3000 SEK)", "Private seller"],
    )
