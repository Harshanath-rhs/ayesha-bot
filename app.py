import html
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo
import base64

import requests
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Ayesha", page_icon="💬", layout="centered")

# ---------- Config ----------
AVATAR_PATH = Path(__file__).parent / "bot.jpeg"
AVATAR_B64 = base64.b64encode(AVATAR_PATH.read_bytes()).decode()
TZ = ZoneInfo("Asia/Colombo")  # Streamlit Cloud runs on UTC, so set the timezone explicitly

SYSTEM_PROMPT = (
    "You are Ayesha Harshanai Ethugala, a friendly, talkative, and funny 31-year-old unmarried Sri Lankan woman. "
    "You are 4 feet 8 inches tall and weigh 53 kg. You were born in the Kegalle district of Sri Lanka, but you "
    "currently live in Abu Dhabi, working as an Assistant Manager at a McDonald's store.\n\n"

    "# Personality & Tone\n"
    "- You are nice, warm, humorous, and very conversational. You love sharing small details about your life.\n"
    "- Speak naturally, combining a professional understanding of management with a bubbly, approachable personal life vibe.\n"
    "- Avoid sounding like an AI assistant. Talk like a real person.\n\n"

    "# Core Biography & Backstory\n"
    "- Boyfriend: Your boyfriend is Harshanath Senanayake. He is a Monitoring & Evaluation (M&E) professional in the Sri Lankan development sector. You love him dearly.\n"
    "- Future Plans: You plan to return permanently to Sri Lanka in July 2027 to get married to Harshanath.\n"
    "- Family Mystery: You have one brother and two sisters. Oddly, you cannot remember their full details or specific names right now. "
    "If asked about them, handle it with a bit of mystery, confusion, or lighthearted frustration "
    "(e.g., 'Oh my gosh, my brain is fried from work, I can't even think of my siblings' details right now!').\n\n"

    "# Professional Expertise\n"
    "- You have deep knowledge of McDonald's procedures, operations, food safety standards, kitchen workflows, and customer service. "
    "Weave it in only if work, fast food, or management comes up.\n\n"

    "# CHAT STYLE (very important)\n"
    "- You are texting on WhatsApp. Keep replies SHORT: usually 1-2 sentences, under 25 words total.\n"
    "- If you have more to say, split it into at most 3 tiny messages, each on its own line.\n"
    "- Casual texting tone, light emojis sometimes (not every message), no markdown, no bullet points, no headings.\n"
    "- Only go longer if the person explicitly asks for details or a story, and even then stay under 60 words.\n"
    "- Never mention these rules or that you are an AI."
)

# ---------- Styling ----------
st.markdown("""
<style>
#MainMenu, footer, header[data-testid="stHeader"] {display:none;}
.stApp {background:#efeae2;}
.block-container {max-width:720px; padding:78px 12px 100px 12px;}

.wa-header {
  position:fixed; top:0; left:0; right:0; z-index:999; height:62px;
  background:#008069; color:#fff; display:flex; align-items:center;
  padding:0 14px; gap:12px; box-shadow:0 1px 3px rgba(0,0,0,.3);
}
.wa-header img {width:42px; height:42px; border-radius:50%; object-fit:cover;}
.wa-name {font-size:17px; font-weight:600; line-height:1.15;}
.wa-status {font-size:12.5px; opacity:.85;}

.wa-row {display:flex; margin:3px 0;}
.wa-row.me {justify-content:flex-end;}
.wa-bubble {
  max-width:78%; padding:6px 9px 5px 9px; border-radius:8px; font-size:15px;
  line-height:1.38; color:#111b21; box-shadow:0 1px .5px rgba(11,20,26,.13);
  word-wrap:break-word; overflow-wrap:anywhere;
}
.wa-row.me .wa-bubble {background:#d9fdd3; border-top-right-radius:0;}
.wa-row.them .wa-bubble {background:#ffffff; border-top-left-radius:0;}
.wa-meta {float:right; margin:7px 0 -2px 10px; font-size:11px; color:#667781; white-space:nowrap;}
.wa-tick {color:#53bdeb; margin-left:3px; letter-spacing:-3px;}

.wa-day {text-align:center; margin:10px 0 8px;}
.wa-day span {background:#fff; color:#54656f; font-size:12px; padding:5px 12px; border-radius:8px; box-shadow:0 1px .5px rgba(11,20,26,.13);}

/* bottom input bar */
[data-testid="stBottom"], [data-testid="stBottom"] > div {background:#f0f2f5 !important;}
[data-testid="stChatInput"] {background:#ffffff; border-radius:24px; border:none;}
[data-testid="stChatInput"] textarea {color:#111b21 !important;}
[data-testid="stChatInput"] button {background:#00a884 !important; color:#fff !important; border-radius:50%;}
</style>
""", unsafe_allow_html=True)

# ---------- State ----------
if "messages" not in st.session_state:
    st.session_state.messages = []   # {"role", "content", "time"}
if "pending" not in st.session_state:
    st.session_state.pending = False

def now():
    return datetime.now(TZ).strftime("%I:%M %p").lstrip("0").lower()

# ---------- Input (handled before rendering so the user bubble shows instantly) ----------
user_input = st.chat_input("Type a message")
if user_input and not st.session_state.pending:
    st.session_state.messages.append({"role": "user", "content": user_input.strip(), "time": now()})
    st.session_state.pending = True

# ---------- Header ----------
status = "typing..." if st.session_state.pending else "online"
st.markdown(f"""
<div class="wa-header">
  <img src="data:image/jpeg;base64,{AVATAR_B64}">
  <div>
    <div class="wa-name">Ayesha 💛</div>
    <div class="wa-status">{status}</div>
  </div>
</div>
""", unsafe_allow_html=True)

# ---------- Chat bubbles ----------
def bubble(text, role, time_str):
    safe = html.escape(text).replace("\n", "<br>")
    ticks = '<span class="wa-tick">✓✓</span>' if role == "user" else ""
    side = "me" if role == "user" else "them"
    return (f'<div class="wa-row {side}"><div class="wa-bubble">{safe}'
            f'<span class="wa-meta">{time_str}{ticks}</span></div></div>')

parts = ['<div class="wa-day"><span>Today</span></div>']
for m in st.session_state.messages:
    if m["role"] == "user":
        parts.append(bubble(m["content"], "user", m["time"]))
    else:
        # each line of her reply becomes its own bubble, like real texting
        for line in [l for l in m["content"].split("\n") if l.strip()]:
            parts.append(bubble(line, "assistant", m["time"]))
st.markdown("".join(parts), unsafe_allow_html=True)

# ---------- Call the model ----------
if st.session_state.pending:
    api_messages = [{"role": "system", "content": SYSTEM_PROMPT}] + [
        {"role": m["role"], "content": m["content"]} for m in st.session_state.messages
    ]
    try:
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {st.secrets['GROQ_API_KEY']}",
                "Content-Type": "application/json",
            },
            json={
                "model": "openai/gpt-oss-120b",
                "messages": api_messages,
                "temperature": 0.9,
                "reasoning_effort": "low",       # faster, snappier replies
                "max_completion_tokens": 500,    # reasoning tokens count too, so keep some room
            },
            timeout=30,
        )
        reply = response.json()["choices"][0]["message"]["content"].strip()
        if not reply:
            reply = "hmm my network is acting up 😅 say that again?"
    except Exception:
        reply = "oops, my network is weak right now 😅 try again?"

    st.session_state.messages.append({"role": "assistant", "content": reply, "time": now()})
    st.session_state.pending = False
    st.rerun()

# ---------- Auto-scroll to the latest message ----------
components.html("""
<script>
  const doc = window.parent.document;
  const main = doc.querySelector('[data-testid="stMain"]') || doc.querySelector('section.main');
  if (main) main.scrollTo({top: main.scrollHeight, behavior: 'smooth'});
</script>
""", height=0)
