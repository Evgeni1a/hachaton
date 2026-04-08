import streamlit as st
import sqlite3
import requests
from datetime import date

# ========== DATABASE ==========
def init_db():
    conn = sqlite3.connect('quotes.db')
    c = conn.cursor()

    c.execute('''
        CREATE TABLE IF NOT EXISTS quotes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            quote TEXT NOT NULL,
            category TEXT DEFAULT 'general',
            fun_fact TEXT DEFAULT '',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    try:
        c.execute("ALTER TABLE quotes ADD COLUMN fun_fact TEXT DEFAULT ''")
        conn.commit()
    except Exception:
        pass

    c.execute('''
        CREATE TABLE IF NOT EXISTS favorites (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            quote TEXT NOT NULL,
            category TEXT DEFAULT 'general',
            fun_fact TEXT DEFAULT '',
            saved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    try:
        c.execute("ALTER TABLE favorites ADD COLUMN fun_fact TEXT DEFAULT ''")
        conn.commit()
    except Exception:
        pass

    c.execute('''
        CREATE TABLE IF NOT EXISTS daily_stats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            stat_date TEXT NOT NULL,
            category TEXT NOT NULL,
            count INTEGER DEFAULT 1,
            UNIQUE(stat_date, category)
        )
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS chat_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            role TEXT NOT NULL,
            message TEXT NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    conn.commit()
    conn.close()


def save_quote(quote, category="general", fun_fact=""):
    conn = sqlite3.connect('quotes.db')
    c = conn.cursor()
    c.execute("INSERT INTO quotes (quote, category, fun_fact) VALUES (?, ?, ?)", (quote, category, fun_fact))
    conn.commit()
    conn.close()


def get_history(limit=50, category=None):
    conn = sqlite3.connect('quotes.db')
    c = conn.cursor()
    if category and category != "all":
        c.execute("SELECT id, quote, category, fun_fact, created_at FROM quotes WHERE category = ? ORDER BY created_at DESC LIMIT ?", (category, limit))
    else:
        c.execute("SELECT id, quote, category, fun_fact, created_at FROM quotes ORDER BY created_at DESC LIMIT ?", (limit,))
    rows = c.fetchall()
    conn.close()
    return rows


def delete_quote_by_id(quote_id):
    conn = sqlite3.connect('quotes.db')
    c = conn.cursor()
    c.execute("DELETE FROM quotes WHERE id = ?", (quote_id,))
    conn.commit()
    conn.close()


def add_favorite(quote, category="general", fun_fact=""):
    conn = sqlite3.connect('quotes.db')
    c = conn.cursor()
    c.execute("INSERT INTO favorites (quote, category, fun_fact) VALUES (?, ?, ?)", (quote, category, fun_fact))
    fav_id = c.lastrowid
    conn.commit()
    conn.close()
    return fav_id


def get_favorites(category=None):
    conn = sqlite3.connect('quotes.db')
    c = conn.cursor()
    if category and category != "all":
        c.execute("SELECT id, quote, category, fun_fact, saved_at FROM favorites WHERE category = ? ORDER BY saved_at DESC", (category,))
    else:
        c.execute("SELECT id, quote, category, fun_fact, saved_at FROM favorites ORDER BY saved_at DESC")
    rows = c.fetchall()
    conn.close()
    return rows


def remove_favorite(fav_id):
    conn = sqlite3.connect('quotes.db')
    c = conn.cursor()
    c.execute("DELETE FROM favorites WHERE id = ?", (fav_id,))
    conn.commit()
    conn.close()


def update_daily_stats(category):
    today = date.today().isoformat()
    conn = sqlite3.connect('quotes.db')
    c = conn.cursor()
    c.execute(
        "INSERT INTO daily_stats (stat_date, category, count) VALUES (?, ?, 1) "
        "ON CONFLICT(stat_date, category) DO UPDATE SET count = count + 1",
        (today, category)
    )
    conn.commit()
    conn.close()


def get_daily_stats():
    today = date.today().isoformat()
    conn = sqlite3.connect('quotes.db')
    c = conn.cursor()
    c.execute("SELECT category, SUM(count) FROM daily_stats WHERE stat_date = ? GROUP BY category", (today,))
    rows = c.fetchall()
    conn.close()
    return rows


def get_today_total():
    today = date.today().isoformat()
    conn = sqlite3.connect('quotes.db')
    c = conn.cursor()
    c.execute("SELECT SUM(count) FROM daily_stats WHERE stat_date = ?", (today,))
    result = c.fetchone()[0]
    conn.close()
    return result or 0


# ========== CHAT ==========
def save_chat_message(role, message):
    conn = sqlite3.connect('quotes.db')
    c = conn.cursor()
    c.execute("INSERT INTO chat_messages (role, message) VALUES (?, ?)", (role, message))
    conn.commit()
    conn.close()


def get_chat_history(limit=100):
    conn = sqlite3.connect('quotes.db')
    c = conn.cursor()
    c.execute("SELECT role, message FROM chat_messages ORDER BY timestamp DESC LIMIT ?", (limit,))
    rows = c.fetchall()
    conn.close()
    return list(reversed(rows))


def clear_chat():
    conn = sqlite3.connect('quotes.db')
    c = conn.cursor()
    c.execute("DELETE FROM chat_messages")
    conn.commit()
    conn.close()


# ========== CATEGORIES ==========
CATEGORIES = {
    "💪 Motivation": "motivation",
    "❤️ Love": "love",
    "🏆 Success": "success",
    "🧠 Wisdom": "wisdom",
    "⚡ Energy": "energy",
    "🌟 General": "general"
}

CATEGORY_PROMPTS = {
    "motivation": "motivational quote about pushing forward, never giving up, discipline, hard work, and achieving goals through effort",
    "love": "warm quote about love, relationships, caring for someone, and emotional connection",
    "success": "quote about winning, reaching the top, achieving success, being the best, and celebrating victories",
    "wisdom": "philosophical quote about life meaning, knowledge, learning from experience, and deep thinking",
    "energy": "high-energy quote about vitality, power, excitement, positive vibes, and being unstoppable",
    "general": "short inspiring quote about life, hope, and personal growth"
}

CATEGORY_DESCRIPTIONS = {
    "motivation": "Quotes about perseverance and discipline",
    "love": "Quotes about love and emotional connection",
    "success": "Quotes about winning and achievement",
    "wisdom": "Philosophical quotes about life and knowledge",
    "energy": "High-energy quotes about vitality and power",
    "general": "General inspiring quotes about life"
}


# ========== NANOBOT MCP CLIENT ==========
NANOBOT_GATEWAY_URL = "http://localhost:8502"
OLLAMA_DIRECT_URL = "http://localhost:11434"


def check_nanobot():
    """Check Nanobot Gateway availability, fallback to direct Ollama."""
    try:
        resp = requests.get(f"{NANOBOT_GATEWAY_URL}/health", timeout=5)
        if resp.status_code == 200:
            return True, "Nanobot Gateway Online", resp.json()
        return check_ollama_fallback()
    except (requests.exceptions.ConnectionError, Exception):
        return check_ollama_fallback()


def check_ollama_fallback():
    """Fallback: check direct Ollama."""
    try:
        resp = requests.get(f"{OLLAMA_DIRECT_URL}/api/tags", timeout=5)
        if resp.status_code == 200:
            models = resp.json().get("models", [])
            model_names = [m.get("name", "") for m in models]
            has_model = any("llama3.2" in m for m in model_names)
            return has_model, f"Ollama: {', '.join(model_names)}", None
        return False, "Ollama: no models", None
    except Exception:
        return False, "Nothing available", None


def nanobot_generate(topic, category="general"):
    """Generate quote via Nanobot MCP tool quotes_generate. Optimized for speed."""
    try:
        resp = requests.post(
            f"{NANOBOT_GATEWAY_URL}/api/tools/quotes_generate",
            json={"topic": topic, "category": category},
            timeout=30,
        )
        if resp.status_code == 200:
            data = resp.json()
            if data.get("status") == "ok":
                return data.get("quote", "")
    except Exception:
        pass
    return generate_quote_ollama_direct(topic, category)


def nanobot_chat(message, chat_history=None):
    """Chat with nanobot via MCP tool quotes_chat. Optimized for speed."""
    context = ""
    if chat_history:
        recent = chat_history[-4:]
        for role, msg in recent:
            context += f"{role}: {msg}\n"

    full_message = f"Context:\n{context}\nMessage: {message}" if context else message

    try:
        resp = requests.post(
            f"{NANOBOT_GATEWAY_URL}/api/tools/quotes_chat",
            json={"message": full_message},
            timeout=30,
        )
        if resp.status_code == 200:
            data = resp.json()
            if data.get("status") == "ok":
                return data.get("response", "")
    except Exception:
        pass
    return chat_ollama_direct(message, chat_history)


def generate_fun_fact(quote):
    """Ask NanoBot for an interesting fact about the given quote. Optimized."""
    prompt = f"ONE short fun fact (max 20 words) related to this quote. Surprising or educational.\n\nQuote: \"{quote}\"\n\nFact:"

    try:
        resp = requests.post(
            f"{NANOBOT_GATEWAY_URL}/api/tools/quotes_chat",
            json={"message": prompt},
            timeout=30,
        )
        if resp.status_code == 200:
            data = resp.json()
            if data.get("status") == "ok":
                return data.get("response", "").strip()
    except Exception:
        pass

    try:
        resp = requests.post(
            f"{OLLAMA_DIRECT_URL}/api/generate",
            json={
                "model": "llama3.2:1b",
                "prompt": prompt,
                "stream": False,
                "options": {"temperature": 0.5, "max_tokens": 40},
            },
            timeout=30,
        )
        if resp.status_code == 200:
            return resp.json().get("response", "").strip()
    except Exception:
        pass

    return "💡 Every great quote reflects a timeless truth about human nature."


def generate_quote_ollama_direct(topic, category="general"):
    """Direct generation via Ollama (fallback). Optimized for speed."""
    prompt = (
        f"Generate ONE short inspirational quote about {topic}. "
        f"Max 20 words. No famous names. ONLY the quote text:\n"
    )

    try:
        resp = requests.post(
            f"{OLLAMA_DIRECT_URL}/api/generate",
            json={
                "model": "llama3.2:1b",
                "prompt": prompt,
                "stream": False,
                "options": {"temperature": 0.7, "max_tokens": 50},
            },
            timeout=30,
        )
        if resp.status_code == 200:
            result = resp.json()
            return result.get("response", "").strip().strip('"\'')
    except Exception:
        pass
    return None


def chat_ollama_direct(message, chat_history=None):
    """Direct chat via Ollama (fallback). Precise and concise."""
    system_prompt = (
        "You are NanoBot, a quote generation robot. "
        "Rules: 1) Answer ONLY what is asked, no greetings or thanks. "
        "2) Be precise and concise, max 3 sentences. "
        "3) When asked for a quote, give exactly ONE quote, nothing else. "
        "4) No filler words. 5) Always respond in English."
    )

    context = ""
    if chat_history:
        for role, msg in chat_history[-3:]:
            context += f"{role}: {msg}\n"

    full_prompt = f"{system_prompt}\n\n{context}User: {message}\nNanoBot:"

    try:
        resp = requests.post(
            f"{OLLAMA_DIRECT_URL}/api/generate",
            json={
                "model": "llama3.2:1b",
                "prompt": full_prompt,
                "stream": False,
                "options": {"temperature": 0.5, "max_tokens": 120},
            },
            timeout=20,
        )
        if resp.status_code == 200:
            return resp.json().get("response", "").strip()
    except Exception:
        pass
    return "🤖 Beep! Could not respond. Try again!"


# ========== NANOBOT CSS ==========
NANOBOT_CSS = """
<style>
    @keyframes pulse {
        0%, 100% { transform: scale(1); }
        50% { transform: scale(1.05); }
    }
    @keyframes blink {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.3; }
    }
    @keyframes slideIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }

    .nanobot-title {
        font-size: 2.5em;
        font-weight: bold;
        color: #ffaa00;
        text-align: center;
        animation: warmGlow 2.5s ease-in-out infinite;
        margin-bottom: 10px;
    }

    @keyframes warmGlow {
        0%, 100% { text-shadow: 0 0 10px #ffaa00, 0 0 20px #ff8800; color: #ffaa00; }
        50% { text-shadow: 0 0 20px #ffaa00, 0 0 40px #ff8800, 0 0 60px #ff6600; color: #ffcc44; }
    }

    .nanobot-container {
        background: transparent;
        border: none;
        padding: 10px;
        box-shadow: none;
    }

    .nanobot-avatar {
        text-align: center;
        font-size: 4em;
        animation: pulse 2s ease-in-out infinite;
        margin: 10px 0;
    }

    .quote-card {
        background: linear-gradient(135deg, #1a1a3e, #2a1a4e);
        border-left: 4px solid #00ffff;
        border-radius: 10px;
        padding: 15px 20px;
        margin: 10px 0;
        animation: slideIn 0.3s ease-out;
    }

    .quote-text {
        font-size: 1.3em;
        color: #e0e0ff;
        font-style: italic;
    }

    .category-badge {
        display: inline-block;
        background: linear-gradient(90deg, #00ffff, #7b2fff);
        color: #0a0a2e;
        padding: 3px 12px;
        border-radius: 20px;
        font-size: 0.8em;
        font-weight: bold;
        margin-top: 8px;
    }

    .fun-fact-box {
        background: linear-gradient(135deg, #1a2a1e, #0a2a3e);
        border-left: 4px solid #00ff88;
        border-radius: 8px;
        padding: 10px 15px;
        margin: 8px 0;
        font-size: 0.95em;
        color: #80ffcc;
    }

    .stat-bar-container {
        background: #1a1a3e;
        border-radius: 10px;
        padding: 10px 15px;
        margin: 5px 0;
    }

    .stat-bar {
        background: linear-gradient(90deg, #00ffff, #7b2fff);
        height: 20px;
        border-radius: 10px;
        transition: width 0.5s ease;
    }

    .status-dot {
        display: inline-block;
        width: 12px;
        height: 12px;
        border-radius: 50%;
        animation: blink 1s ease-in-out infinite;
    }

    .status-dot.online { background: #00ff00; }
    .status-dot.offline { background: #ff0000; }

    .chat-bubble-user {
        background: #2a2a5e;
        color: #e0e0ff;
        padding: 10px 15px;
        border-radius: 15px 15px 0 15px;
        margin: 5px 20px 5px 40px;
        border: 1px solid #7b2fff;
    }

    .chat-bubble-bot {
        background: #1a2a3e;
        color: #00ffff;
        padding: 10px 15px;
        border-radius: 15px 15px 15px 0;
        margin: 5px 40px 5px 20px;
        border: 1px solid #00ffff;
    }

    .stButton button {
        background: linear-gradient(90deg, #00ffff, #7b2fff);
        color: #0a0a2e;
        border: none;
        border-radius: 10px;
        font-weight: bold;
        transition: all 0.3s;
    }
    .stButton button:hover {
        box-shadow: 0 0 15px rgba(0, 255, 255, 0.5);
        transform: translateY(-2px);
    }

    .block-container { background: transparent; }
    main { background: linear-gradient(180deg, #0a0a2e 0%, #1a0a2e 100%); }
    [data-testid="stSidebar"] { background: #0d0d30; }

    .category-filter {
        background: #1a1a3e;
        border-radius: 8px;
        padding: 10px;
        margin-bottom: 15px;
    }
</style>
"""


# ========== MAIN APP ==========
def main():
    st.set_page_config(
        page_title="🤖 Nanobot Quote Generator",
        page_icon="🤖",
        layout="centered"
    )

    st.markdown(NANOBOT_CSS, unsafe_allow_html=True)
    init_db()

    category_labels = {
        "💪 Motivation": "motivation",
        "❤️ Love": "love",
        "🏆 Success": "success",
        "🧠 Wisdom": "wisdom",
        "⚡ Energy": "energy",
        "🌟 Any": "general"
    }
    reverse_labels = {v: k for k, v in category_labels.items()}

    # ===== Sidebar =====
    with st.sidebar:
        st.markdown('<div class="nanobot-avatar">🤖</div>', unsafe_allow_html=True)
        st.markdown('<div style="text-align:center;color:#00ffff;font-size:1.1em;font-weight:bold;">NANOBOT</div>', unsafe_allow_html=True)

        connected, status_text, extra = check_nanobot()

        if connected:
            st.markdown('<span class="status-dot online"></span> <span style="color:#00ff00;">Nanobot Online</span>', unsafe_allow_html=True)
            st.caption(f"📦 {status_text}")
        else:
            st.markdown('<span class="status-dot offline"></span> <span style="color:#ff0000;">Nothing Available</span>', unsafe_allow_html=True)
            st.error("❌ **How to fix:**\n\n1. Start Ollama: `ollama serve`\n2. Or start Nanobot Gateway\n3. Make sure model exists: `ollama pull llama3.2:1b`")

        st.divider()

        st.markdown("### ⚙️ Settings")
        st.caption("💡 Run `ollama serve` in your terminal")

        st.divider()
        st.metric("📊 Quotes Today", get_today_total())

    # ===== Header =====
    st.markdown('<div style="text-align:center;padding:15px 0 5px 0;">', unsafe_allow_html=True)
    st.markdown('<div class="nanobot-title">Nanobot Quote Generator</div>', unsafe_allow_html=True)
    st.markdown('<p style="text-align:center;color:#a0a0ff;font-size:1.1em;margin-top:-5px;">Small robot, big ideas</p>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # ===== Tabs =====
    tab_generator, tab_chat, tab_history, tab_favorites, tab_stats = st.tabs([
        "🎲 Generator",
        "💬 Chat",
        "📜 History",
        "⭐ Favorites",
        "📊 Statistics"
    ])

    # ===== GENERATOR TAB =====
    with tab_generator:
        st.markdown("### Choose your mood:")

        selected_cat = st.session_state.get('selected_category', 'general')

        cols = st.columns(3)
        for i, (label, key) in enumerate(category_labels.items()):
            with cols[i % 3]:
                btn_type = "primary" if key == selected_cat else "secondary"
                if st.button(label, type=btn_type, use_container_width=True, key=f"cat_{key}"):
                    st.session_state.selected_category = key
                    st.rerun()

        st.markdown("---")

        if st.button("Generate Quote", type="primary", use_container_width=True):
            cat = st.session_state.selected_category
            if not connected:
                st.error("❌ Nanobot unavailable! Start Ollama or Nanobot Gateway")
            else:
                topic = category_labels.get(cat, "general")
                quote = nanobot_generate(topic, cat)

                if not quote:
                    st.error("Failed to generate a quote")
                else:
                    st.session_state.current_quote = quote
                    st.session_state.current_category = cat
                    save_quote(quote, cat, "")
                    update_daily_stats(cat)

        if 'current_quote' in st.session_state:
            st.markdown("---")
            cat = st.session_state.get('current_category', 'general')
            cat_display = reverse_labels.get(cat, cat)

            st.markdown(f'''
                <div class="quote-card">
                    <div class="quote-text">"{st.session_state.current_quote}"</div>
                    <span class="category-badge">{cat_display}</span>
                </div>
            ''', unsafe_allow_html=True)

            cols = st.columns(2)
            with cols[0]:
                if st.button("❤️ Add to Favorites", use_container_width=True, key="add_fav_btn"):
                    add_favorite(st.session_state.current_quote, st.session_state.get('current_category', 'general'), st.session_state.get('current_fun_fact', ''))
                    st.toast("Added to favorites!", icon="❤️")
            with cols[1]:
                if st.button("🔄 Regenerate", use_container_width=True):
                    cat = st.session_state.selected_category
                    topic = category_labels.get(cat, "general")
                    quote = nanobot_generate(topic, cat)
                    if quote:
                        st.session_state.current_quote = quote
                        st.session_state.current_category = cat
                        save_quote(quote, cat, "")
                        update_daily_stats(cat)
                        st.rerun()

    # ===== CHAT TAB =====
    with tab_chat:
        st.markdown("### 💬 Chat with NanoBot")
        st.caption("Ask for quotes, explanations, or just chat!")

        if not connected:
            st.error("🔴 Nanobot unavailable. Check:")
            st.code("ollama serve")
            st.code("ollama pull llama3.2:1b")
            if st.button("🔄 Recheck Nanobot"):
                st.rerun()
            st.stop()

        if "chat_messages" not in st.session_state:
            st.session_state.chat_messages = get_chat_history()

        chat_container = st.container()
        with chat_container:
            for role, msg in st.session_state.chat_messages:
                if role == "user":
                    st.markdown(f'<div class="chat-bubble-user">🧑 {msg}</div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="chat-bubble-bot">🤖 {msg}</div>', unsafe_allow_html=True)

        st.markdown("---")

        user_input = st.chat_input("Type a message to NanoBot...")
        if user_input:
            if not connected:
                bot_response = "❌ Nanobot unavailable. Start Ollama or Nanobot Gateway."
                save_chat_message("user", user_input)
                save_chat_message("bot", bot_response)
                st.session_state.chat_messages.append(("user", user_input))
                st.session_state.chat_messages.append(("bot", bot_response))
                st.rerun()
            else:
                save_chat_message("user", user_input)
                st.session_state.chat_messages.append(("user", user_input))

                bot_response = nanobot_chat(user_input, st.session_state.chat_messages)

                save_chat_message("bot", bot_response)
                st.session_state.chat_messages.append(("bot", bot_response))
                st.rerun()

        if st.button("🗑️ Clear Chat", use_container_width=True):
            clear_chat()
            st.session_state.chat_messages = []
            st.rerun()

    # ===== HISTORY TAB =====
    with tab_history:
        st.markdown("### Quote History")

        # Category filter - default to All
        filter_options = ["All"] + list(category_labels.keys())
        selected_filter = st.selectbox(
            "Filter by category:",
            options=filter_options,
            index=0,
            key="history_filter"
        )

        if selected_filter == "All":
            filter_key = "all"
        else:
            filter_key = category_labels[selected_filter]

        history = get_history(category=filter_key)
        if not history:
            if filter_key == "all":
                st.info("No quotes generated yet. Generate your first one!")
            else:
                st.info(f"No quotes in the {selected_filter.lower()} category yet.")
        else:
            for idx, (qid, quote, cat, fun_fact, date) in enumerate(history):
                cat_display = reverse_labels.get(cat, cat)

                st.markdown(f'''
                    <div class="quote-card">
                        <div class="quote-text">"{quote}"</div>
                        <span class="category-badge">{cat_display}</span>
                        <div style="color:#8080aa;font-size:0.85em;margin-top:5px;">📅 {date}</div>
                    </div>
                ''', unsafe_allow_html=True)

                if fun_fact:
                    st.markdown(f'<div class="fun-fact-box">💡 {fun_fact}</div>', unsafe_allow_html=True)

                cols = st.columns([1, 1])
                with cols[0]:
                    if st.button("❤️ Favorite", use_container_width=True, key=f"hist_fav_{qid}"):
                        add_favorite(quote, cat, fun_fact)
                        st.toast("Added to favorites!", icon="❤️")
                with cols[1]:
                    if st.button("🗑️ Delete", use_container_width=True, key=f"hist_del_{qid}"):
                        delete_quote_by_id(qid)
                        st.rerun()

    # ===== FAVORITES TAB =====
    with tab_favorites:
        st.markdown("### Favorites")

        # Category filter
        filter_options = ["All"] + list(category_labels.keys())
        selected_filter = st.selectbox(
            "Filter by category:",
            options=filter_options,
            index=0,
            key="fav_filter"
        )

        if selected_filter == "All":
            filter_key = "all"
        else:
            filter_key = category_labels[selected_filter]

        favorites = get_favorites(category=filter_key)
        if not favorites:
            if filter_key == "all":
                st.info("No favorites yet. Save quotes you like!")
            else:
                st.info(f"No favorites in the {selected_filter.lower()} category.")
        else:
            for fav_id, quote, cat, fun_fact, date in favorites:
                cat_display = reverse_labels.get(cat, cat)

                st.markdown(f'''
                    <div class="quote-card">
                        <div class="quote-text">"{quote}"</div>
                        <span class="category-badge">{cat_display}</span>
                        <div style="color:#8080aa;font-size:0.85em;margin-top:5px;">⭐ {date}</div>
                    </div>
                ''', unsafe_allow_html=True)

                if fun_fact:
                    st.markdown(f'<div class="fun-fact-box">💡 {fun_fact}</div>', unsafe_allow_html=True)

                if st.button("🗑️ Remove", use_container_width=True, key=f"del_fav_{fav_id}"):
                    remove_favorite(fav_id)
                    st.rerun()

    # ===== STATS TAB =====
    with tab_stats:
        st.markdown("### Today's Statistics")

        total = get_today_total()
        st.metric("Total Quotes Today", total)

        if total == 0:
            st.info("No quotes generated today. Time to create some!")
        else:
            stats = get_daily_stats()
            if stats:
                max_count = max(count for _, count in stats)

                st.markdown("#### By Category:")
                for cat, count in stats:
                    cat_display = reverse_labels.get(cat, cat)

                    bar_width = int((count / max_count) * 100) if max_count > 0 else 0
                    st.markdown(f'''
                        <div class="stat-bar-container">
                            <div style="color:#e0e0ff;margin-bottom:5px;">{cat_display} - {count}</div>
                            <div class="stat-bar" style="width:{bar_width}%;"></div>
                        </div>
                    ''', unsafe_allow_html=True)


if __name__ == "__main__":
    main()
