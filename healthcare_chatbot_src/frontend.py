import streamlit as st
import requests
import json
import time
from datetime import datetime
from typing import Dict, List, Optional, Any
import re

# Configuration
API_BASE_URL = "http://localhost:8000/api/v1"

# Page configuration
st.set_page_config(
    page_title="Medical Services ChatBot",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        text-align: center;
        color: #1f77b4;
        font-size: 2.5rem;
        margin-bottom: 2rem;
    }
    .chat-message {
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 10px;
    }
    .user-message {
        background-color: #e3f2fd;
        border-left: 5px solid #2196f3;
    }
    .bot-message {
        background-color: #f3e5f5;
        border-left: 5px solid #9c27b0;
    }
    .suggested-question {
        background-color: #e8f5e8;
        border: 1px solid #4caf50;
        border-radius: 20px;
        padding: 0.5rem 1rem;
        margin: 0.25rem;
        cursor: pointer;
        display: inline-block;
    }
    .suggested-question:hover {
        background-color: #c8e6c9;
    }
    .language-switch {
        position: fixed;
        top: 1rem;
        right: 1rem;
        z-index: 1000;
    }
    
    /* RTL Support for Hebrew */
    .rtl-text {
        direction: rtl !important;
        text-align: right !important;
        unicode-bidi: bidi-override !important;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif !important;
    }
    
    .rtl-input {
        direction: rtl !important;
        text-align: right !important;
        unicode-bidi: bidi-override !important;
    }
    
    /* Hebrew-specific improvements */
    .rtl-text strong {
        font-weight: bold !important;
        color: #333 !important;
    }
    
    .rtl-text br {
        display: block !important;
        margin: 0.5em 0 !important;
    }
    
    /* Ensure proper spacing for Hebrew text */
    .rtl-text .chat-message {
        padding-right: 1.5rem !important;
        padding-left: 1rem !important;
    }
    
    /* Override Streamlit's default text alignment for RTL */
    .rtl-text p, .rtl-text div, .rtl-text span {
        text-align: right !important;
        direction: rtl !important;
    }
    
    /* Force RTL for chat messages */
    .chat-message.rtl-text {
        text-align: right !important;
        direction: rtl !important;
    }
    
    /* Override Streamlit's default button alignment */
    .rtl-text button {
        text-align: center !important;
        direction: ltr !important; /* Keep buttons LTR for better UX */
    }
    
    /* Fix for numbers and percentages in Hebrew RTL */
    .rtl-text .number, .rtl-text .percentage {
        direction: ltr !important;
        unicode-bidi: embed !important;
        display: inline-block !important;
    }
    
    /* Ensure percentages display correctly */
    .rtl-text .percentage {
        direction: ltr !important;
        unicode-bidi: embed !important;
    }
    
    /* Fix for any text containing numbers or percentages */
    .rtl-text {
        unicode-bidi: plaintext !important;
    }
    
    /* Additional fixes for Hebrew text with numbers */
    .rtl-text {
        /* Use plaintext to prevent bidirectional text issues */
        unicode-bidi: plaintext !important;
    }
    
    /* Target specific patterns that commonly cause issues */
    .rtl-text * {
        /* Ensure child elements inherit the plaintext behavior */
        unicode-bidi: inherit !important;
    }
    
    /* Force LTR for any content that looks like numbers or percentages */
    .rtl-text span:contains("%"),
    .rtl-text span:contains("0"),
    .rtl-text span:contains("1"),
    .rtl-text span:contains("2"),
    .rtl-text span:contains("3"),
    .rtl-text span:contains("4"),
    .rtl-text span:contains("5"),
    .rtl-text span:contains("6"),
    .rtl-text span:contains("7"),
    .rtl-text span:contains("8"),
    .rtl-text span:contains("9") {
        direction: ltr !important;
        unicode-bidi: embed !important;
    }
    
    /* Custom styling for better input experience */
    .stTextArea textarea {
        font-size: 16px;
        line-height: 1.5;
        resize: vertical;
    }
    
    .stButton button {
        font-weight: bold;
        transition: all 0.3s ease;
    }
    
    .stButton button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    
    /* Link styling for both RTL and LTR */
    .chat-message a {
        color: #1976d2 !important;
        text-decoration: underline !important;
        font-weight: 500 !important;
        transition: color 0.3s ease !important;
    }
    
    .chat-message a:hover {
        color: #1565c0 !important;
        text-decoration: none !important;
    }
    
    /* Ensure links work properly in RTL text */
    .rtl-text a {
        direction: ltr !important;
        unicode-bidi: embed !important;
        display: inline-block !important;
    }
</style>

<script>
// Add Enter key support for text area
document.addEventListener('DOMContentLoaded', function() {
    const textAreas = document.querySelectorAll('textarea');
    textAreas.forEach(function(textarea) {
        textarea.addEventListener('keydown', function(e) {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                // Find and click the submit button
                const form = textarea.closest('form');
                if (form) {
                    const submitButton = form.querySelector('button[type="submit"]');
                    if (submitButton) {
                        submitButton.click();
                    }
                }
            }
        });
    });
    
    // Force RTL for Hebrew text elements
    function enforceRTL() {
        const rtlElements = document.querySelectorAll('.rtl-text');
        rtlElements.forEach(function(element) {
            element.style.direction = 'rtl';
            element.style.textAlign = 'right';
            element.style.unicodeBidi = 'plaintext';
            
            // Apply RTL to all child text elements
            const textElements = element.querySelectorAll('p, div, span, h1, h2, h3, h4, h5, h6');
            textElements.forEach(function(textEl) {
                textEl.style.direction = 'rtl';
                textEl.style.textAlign = 'right';
                textEl.style.unicodeBidi = 'plaintext';
            });
            
            // Fix numbers and percentages to display correctly
            const textContent = element.textContent;
            if (textContent) {
                // Find percentages and wrap them in spans with proper direction
                const percentagePattern = /(\d+%)/g;
                let updatedContent = textContent.replace(percentagePattern, function(match) {
                    return '<span style="direction: ltr; unicode-bidi: embed; display: inline-block;">' + match + '</span>';
                });
                
                // Find phone numbers (patterns like *3555, 1-700-50-53-53)
                const phonePattern = /(\*?\d+(?:-\d+)*)/g;
                updatedContent = updatedContent.replace(phonePattern, function(match) {
                    return '<span style="direction: ltr; unicode-bidi: embed; display: inline-block;">' + match + '</span>';
                });
                
                // Find standalone numbers
                const numberPattern = /(\b\d+\b)/g;
                updatedContent = updatedContent.replace(numberPattern, function(match) {
                    return '<span style="direction: ltr; unicode-bidi: embed;">' + match + '</span>';
                });
                
                // If content was updated, apply it
                if (updatedContent !== textContent) {
                    element.innerHTML = updatedContent;
                }
            }
        });
        
        // Force RTL for textareas
        const textareas = document.querySelectorAll('.stTextArea textarea');
        textareas.forEach(function(textarea) {
            textarea.style.direction = 'rtl';
            textarea.style.textAlign = 'right';
            textarea.style.unicodeBidi = 'bidi-override';
        });
    }
    
    // Run RTL enforcement immediately and after a short delay
    enforceRTL();
    setTimeout(enforceRTL, 100);
    setTimeout(enforceRTL, 500);
    
    // Monitor for dynamic content changes
    const observer = new MutationObserver(function(mutations) {
        mutations.forEach(function(mutation) {
            if (mutation.type === 'childList') {
                setTimeout(enforceRTL, 50);
            }
        });
    });
    
    observer.observe(document.body, {
        childList: true,
        subtree: true
    });
});
</script>
""", unsafe_allow_html=True)

# Initialize session state
if 'conversation_history' not in st.session_state:
    st.session_state.conversation_history = []
if 'current_phase' not in st.session_state:
    st.session_state.current_phase = "info_collection"
if 'user_info' not in st.session_state:
    st.session_state.user_info = None
if 'language' not in st.session_state:
    st.session_state.language = "he"
if 'user_info_complete' not in st.session_state:
    st.session_state.user_info_complete = False
# Removed input_text session state - not needed with dynamic keys

# Language dictionaries
LANGUAGES = {
    "he": {
        "title": "צ'אטבוט שירותי בריאות",
        "subtitle": "מערכת מידע על שירותי בריאות בישראל",
        "start_info_collection": "התחל שיחה",
        "send_message": "שלח הודעה",
        "type_message": "הקלד את הודעתך כאן...",
        "loading": "טוען...",
        "error": "שגיאה",
        "success": "הצלחה",
        "info": "מידע",
        "warning": "אזהרה",
        "user_info_collected": "מידע אישי נאסף בהצלחה!",
        "suggested_questions": "שאלות מומלצות:",
        "clear_conversation": "נקה שיחה",
        "export_conversation": "ייצא שיחה",
        "settings": "הגדרות",
        "language": "שפה",
        "hebrew": "עברית",
        "english": "English",
        "api_status": "סטטוס API",
        "connected": "מחובר",
        "disconnected": "מנותק",
        "health_check": "בדיקת בריאות",
        "services_available": "שירותים זמינים",
        "conversation_stats": "סטטיסטיקות שיחה",
        "total_messages": "סה\"כ הודעות",
        "user_messages": "הודעות משתמש",
        "bot_messages": "הודעות בוט",
        "session_duration": "משך הפעלה",
        "welcome_title": "שלום! אני אלון, העוזר הרפואי שלך",
        "welcome_subtitle": "אני כאן כדי לעזור לך עם שאלות על שירותי הבריאות שלך",
        "welcome_info": "כדי שאוכל לעזור לך בצורה הטובה ביותר, אני צריך את המידע הבא:",
        "welcome_list": [
            "שם מלא",
            "מספר תעודת זהות",
            "מגדר",
            "גיל",
            "קופת חולים",
            "מספר כרטיס קופת חולים",
            "רמת ביטוח"
        ]
    },
    "en": {
        "title": "Medical Services ChatBot",
        "subtitle": "Healthcare Services Information System in Israel",
        "start_info_collection": "Start Conversation",
        "send_message": "Send Message",
        "type_message": "Type your message here...",
        "loading": "Loading...",
        "error": "Error",
        "success": "Success",
        "info": "Information",
        "warning": "Warning",
        "user_info_collected": "Personal information collected successfully!",
        "suggested_questions": "Suggested Questions:",
        "clear_conversation": "Clear Conversation",
        "export_conversation": "Export Conversation",
        "settings": "Settings",
        "language": "Language",
        "hebrew": "עברית",
        "english": "English",
        "api_status": "API Status",
        "connected": "Connected",
        "disconnected": "Disconnected",
        "health_check": "Health Check",
        "services_available": "Available Services",
        "conversation_stats": "Conversation Statistics",
        "total_messages": "Total Messages",
        "user_messages": "User Messages",
        "bot_messages": "Bot Messages",
        "session_duration": "Session Duration",
        "welcome_title": "Hello! I'm Alon, your medical assistant",
        "welcome_subtitle": "I'm here to help you with questions about your healthcare services",
        "welcome_info": "To help you best, I need the following information:",
        "welcome_list": [
            "Full name",
            "ID number",
            "Gender",
            "Age",
            "HMO",
            "HMO card number",
            "Insurance tier"
        ]
    }
}

def get_text(key: str) -> str:
    """Get text in current language"""
    return LANGUAGES[st.session_state.language].get(key, key)

def check_api_health() -> bool:
    """Check if the API is running and healthy"""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        return response.status_code == 200
    except:
        return False

def send_chat_message(message: str) -> Optional[Dict[str, Any]]:
    """Send message to the chatbot API"""
    try:
        # Handle conversation history - convert to proper format
        conversation_history = []
        for msg in st.session_state.conversation_history:
            if isinstance(msg, dict):
                conversation_history.append(msg)
            else:
                # If it's an object with .dict() method, use it
                try:
                    conversation_history.append(msg.dict())
                except AttributeError:
                    # Fallback to basic dict conversion
                    conversation_history.append({
                        "role": getattr(msg, "role", "unknown"),
                        "content": getattr(msg, "content", str(msg)),
                        "timestamp": getattr(msg, "timestamp", None)
                    })
        
        # Handle user_info correctly whether it's a dict or Pydantic model
        user_info_data = None
        if st.session_state.user_info:
            if hasattr(st.session_state.user_info, 'dict'):
                # It's a Pydantic model
                user_info_data = st.session_state.user_info.dict()
            else:
                # It's already a dictionary
                user_info_data = st.session_state.user_info
        
        payload = {
            "message": message,
            "user_info": user_info_data,
            "conversation_history": conversation_history,
            "phase": st.session_state.current_phase,
            "language": st.session_state.language
        }
        
        response = requests.post(f"{API_BASE_URL}/chat", json=payload, timeout=30)
        
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"API Error: {response.status_code} - {response.text}")
            return None
            
    except requests.exceptions.RequestException as e:
        st.error(f"Connection Error: {str(e)}")
        return None

def add_message_to_history(role: str, content: str):
    """Add message to conversation history"""
    timestamp = datetime.now().isoformat()
    message = {
        "role": role,
        "content": content,
        "timestamp": timestamp
    }
    st.session_state.conversation_history.append(message)

def clear_conversation():
    """Clear conversation history and reset state"""
    st.session_state.conversation_history = []
    st.session_state.current_phase = "info_collection"
    st.session_state.user_info = None
    st.session_state.user_info_complete = False
    # Input will automatically clear due to dynamic key change

def export_conversation():
    """Export conversation to JSON file"""
    if not st.session_state.conversation_history:
        st.warning("No conversation to export")
        return
    
    # Handle user_info correctly whether it's a dict or Pydantic model
    user_info_data = None
    if st.session_state.user_info:
        if hasattr(st.session_state.user_info, 'dict'):
            # It's a Pydantic model
            user_info_data = st.session_state.user_info.dict()
        else:
            # It's already a dictionary
            user_info_data = st.session_state.user_info
    
    conversation_data = {
        "export_timestamp": datetime.now().isoformat(),
        "language": st.session_state.language,
        "phase": st.session_state.current_phase,
        "user_info": user_info_data,
        "conversation": st.session_state.conversation_history
    }
    
    # Create download button
    st.download_button(
        label=get_text("export_conversation"),
        data=json.dumps(conversation_data, ensure_ascii=False, indent=2),
        file_name=f"medical_chatbot_conversation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
        mime="application/json"
    )

def display_conversation():
    """Display conversation history"""
    for message in st.session_state.conversation_history:
        # Determine if text should be RTL (Hebrew)
        is_hebrew = st.session_state.language == "he"
        rtl_class = "rtl-text" if is_hebrew else ""
        
        # Get the content and make URLs clickable (simple approach)
        content = message["content"]
        
        # Simple URL detection and conversion to clickable links
        import re
        # Find URLs and make them clickable
        url_pattern = r'https?://[^\s<>"]+'
        content = re.sub(url_pattern, r'<a href="\g<0>" target="_blank" style="color: #1976d2; text-decoration: underline;">\g<0></a>', content)
        
        if message["role"] == "user":
            st.markdown(f"""
            <div class="chat-message user-message {rtl_class}">
                <strong>👤 {get_text('user_messages')}:</strong><br>
                {content}
            </div>
            """, unsafe_allow_html=True)
        elif message["role"] == "assistant":
            st.markdown(f"""
            <div class="chat-message bot-message {rtl_class}">
                <strong>🤖 {get_text('bot_messages')}:</strong><br>
                {content}
            </div>
            """, unsafe_allow_html=True)

def main():
    # Language switcher
    with st.sidebar:
        # Determine if sidebar should be RTL (Hebrew)
        is_hebrew = st.session_state.language == "he"
        sidebar_rtl_class = "rtl-text" if is_hebrew else ""
        
        st.markdown(f"<div class='{sidebar_rtl_class}'>## {get_text('settings')}</div>", unsafe_allow_html=True)
        new_language = st.selectbox(
            get_text("language"),
            options=["he", "en"],
            index=0 if st.session_state.language == "he" else 1,
            format_func=lambda x: LANGUAGES[x]["hebrew"] if x == "he" else LANGUAGES[x]["english"]
        )
        
        if new_language != st.session_state.language:
            st.session_state.language = new_language
            st.rerun()
    
    # Main header
    # Determine if header should be RTL (Hebrew)
    is_hebrew = st.session_state.language == "he"
    header_rtl_class = "rtl-text" if is_hebrew else ""
    
    # Apply comprehensive RTL styling for Hebrew
    if is_hebrew:
        st.markdown("""
        <style>
        /* Force RTL for the entire page when Hebrew is selected */
        .main .block-container {
            direction: rtl !important;
        }
        
        /* Override Streamlit's default text alignment */
        .main .block-container p,
        .main .block-container div,
        .main .block-container span,
        .main .block-container h1,
        .main .block-container h2,
        .main .block-container h3 {
            text-align: right !important;
            direction: rtl !important;
        }
        
        /* Keep headers centered but with RTL text flow */
        .main-header.rtl-text {
            text-align: center !important;
            direction: rtl !important;
        }
        
        /* Force RTL for all text elements */
        .rtl-text, .rtl-text * {
            direction: rtl !important;
            text-align: right !important;
        }
        
        /* Exception for buttons - keep them centered */
        .rtl-text button {
            text-align: center !important;
            direction: ltr !important;
        }
        </style>
        """, unsafe_allow_html=True)
    
    st.markdown(f"<h1 class='main-header {header_rtl_class}'>{get_text('title')}</h1>", unsafe_allow_html=True)
    st.markdown(f"<h3 style='text-align: center; color: #666;' class='{header_rtl_class}'>{get_text('subtitle')}</h3>", unsafe_allow_html=True)
    
    # API status check
    api_healthy = check_api_health()
    if not api_healthy:
        # Apply RTL styling to error message if Hebrew
        if st.session_state.language == "he":
            st.markdown(f"""
            <div class="rtl-text">
                <div style="color: #d32f2f; font-weight: bold;">⚠️ {get_text('api_status')}: {get_text('disconnected')}</div>
            </div>
            """, unsafe_allow_html=True)
            st.markdown(f"""
            <div class="rtl-text">
                <div style="color: #1976d2;">אנא ודא שהשרת האחורי פועל על http://localhost:8000</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.error(f"⚠️ {get_text('api_status')}: {get_text('disconnected')}")
            st.info("Please make sure the backend API is running on http://localhost:8000")
        return
    
    # Sidebar with controls and stats
    with st.sidebar:
        # Determine if sidebar should be RTL (Hebrew)
        is_hebrew = st.session_state.language == "he"
        sidebar_rtl_class = "rtl-text" if is_hebrew else ""
        
        # Apply RTL styling to success message if Hebrew
        if is_hebrew:
            st.markdown(f"""
            <div class="rtl-text">
                <div style="color: #2e7d32; font-weight: bold;">✅ {get_text('api_status')}: {get_text('connected')}</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.success(f"✅ {get_text('api_status')}: {get_text('connected')}")
        
        # Health check button
        if st.button(get_text("health_check")):
            health_response = requests.get(f"{API_BASE_URL}/health")
            if health_response.status_code == 200:
                health_data = health_response.json()
                st.json(health_data)
        
        # Conversation statistics
        st.markdown(f"<div class='{sidebar_rtl_class}'>## {get_text('conversation_stats')}</div>", unsafe_allow_html=True)
        total_messages = len(st.session_state.conversation_history)
        user_messages = len([msg for msg in st.session_state.conversation_history if msg["role"] == "user"])
        bot_messages = len([msg for msg in st.session_state.conversation_history if msg["role"] == "assistant"])
        
        st.metric(get_text("total_messages"), total_messages)
        st.metric(get_text("user_messages"), user_messages)
        st.metric(get_text("bot_messages"), bot_messages)
        
        # Control buttons
        st.markdown(f"<div class='{sidebar_rtl_class}'>## Controls</div>", unsafe_allow_html=True)
        if st.button(get_text("clear_conversation")):
            clear_conversation()
            st.rerun()
        
        export_conversation()
    
    # Display conversation history
    if st.session_state.conversation_history:
        display_conversation()
    else:
        # Show initial welcome message when no conversation exists
        welcome_message = f"""{get_text('welcome_title')}

{get_text('welcome_subtitle')}"""
        
        # Determine if text should be RTL (Hebrew)
        is_hebrew = st.session_state.language == "he"
        rtl_class = "rtl-text" if is_hebrew else ""
        
        st.markdown(f"""
        <div class="chat-message bot-message {rtl_class}">
            <strong>🤖 {get_text('bot_messages')}:</strong><br>
            {welcome_message}
        </div>
        """, unsafe_allow_html=True)
    
    # Chat input
    st.markdown("---")
    
    # Use a form for better input handling and Enter key support
    with st.form(key=f"chat_form_{len(st.session_state.conversation_history)}"):
        # Message input with proper clearing mechanism
        # Use a unique key that changes when we want to clear the input
        input_key = f"user_input_{len(st.session_state.conversation_history)}"
        
        # Determine if input should be RTL (Hebrew)
        is_hebrew = st.session_state.language == "he"
        
        user_message = st.text_area(
            get_text("type_message"),
            height=100,
            key=input_key,
            placeholder=get_text("type_message"),
            max_chars=1000
        )
        
        # Apply RTL styling to the textarea if Hebrew
        if is_hebrew:
            st.markdown("""
            <style>
            /* Target Streamlit textarea specifically */
            .stTextArea textarea {
                direction: rtl !important;
                text-align: right !important;
                unicode-bidi: bidi-override !important;
            }
            
            /* Target the textarea container */
            .stTextArea > div > div > textarea {
                direction: rtl !important;
                text-align: right !important;
                unicode-bidi: bidi-override !important;
            }
            
            /* Force RTL for the textarea input */
            .stTextArea textarea[data-testid="stTextArea"] {
                direction: rtl !important;
                text-align: right !important;
                unicode-bidi: bidi-override !important;
            }
            
            /* Override any Streamlit default styles */
            .stTextArea textarea,
            .stTextArea > div > div > textarea,
            .stTextArea textarea[data-testid="stTextArea"] {
                direction: rtl !important;
                text-align: right !important;
                unicode-bidi: bidi-override !important;
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif !important;
            }
            </style>
            """, unsafe_allow_html=True)
        
        # Show character count
        if user_message:
            char_count = len(user_message)
            # Apply RTL styling to character count if Hebrew
            if is_hebrew:
                st.markdown(f"""
                <div class="rtl-text">
                    <small>תווים: {char_count}/1000</small>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.caption(f"Characters: {char_count}/1000")
        
        col1, col2 = st.columns([1, 4])
        
        with col1:
            send_button = st.form_submit_button(get_text("send_message"), type="primary")
        
        with col2:
            if not st.session_state.conversation_history:
                start_button = st.form_submit_button(get_text("start_info_collection"))
            else:
                start_button = False
    
    # Handle user input
    if send_button and user_message.strip():
        # Add user message to history
        add_message_to_history("user", user_message.strip())
        # Input will automatically clear due to dynamic key change
        
        # Send to API with better visual feedback
        with st.spinner(f"🤖 {get_text('loading')}..."):
            response = send_chat_message(user_message.strip())
        
        if response:
            # Add bot response to history
            add_message_to_history("assistant", response["response"])
            
            # Update phase if needed (internal logic only)
            if response["phase"] != st.session_state.current_phase:
                st.session_state.current_phase = response["phase"]
                if response["phase"] == "qa":
                    st.success(get_text("user_info_collected"))
            
            # Update user info completion status
            st.session_state.user_info_complete = response["user_info_complete"]
            
            # Store user_info if provided (important for QA phase)
            if "user_info" in response and response["user_info"]:
                st.session_state.user_info = response["user_info"]
            
            # Rerun to refresh the interface
            st.rerun()
    
    elif start_button:
        # Start information collection with bulk request
        if st.session_state.language == "he":
            initial_message = """מעולה! עכשיו אני יכול לעזור לך עם שירותי הבריאות שלך.

אנא ספק את הפרטים הבאים:
1. שם פרטי ושם משפחה
2. מספר תעודת זהות (9 ספרות)
3. מגדר
4. גיל
5. שם קופת החולים (מכבי/מאוחדת/כללית)
6. מספר כרטיס קופת החולים (9 ספרות)
7. רמת ביטוח (זהב/כסף/ארד)

אנא ספק את כל המידע הזה בבת אחת."""
        else:
            initial_message = """Great! Now I can help you with your healthcare services.

Please provide the following details:
1. First and last name
2. ID number (9 digits)
3. Gender
4. Age
5. HMO name (Maccabi/Meuhedet/Clalit)
6. HMO card number (9 digits)
7. Insurance tier (Gold/Silver/Bronze)

Please provide all this information at once."""
        
        add_message_to_history("assistant", initial_message)
        st.rerun()
    
    # Display suggested questions if available
    if (st.session_state.current_phase == "qa" and 
        st.session_state.conversation_history and 
        any(msg["role"] == "assistant" for msg in st.session_state.conversation_history)):
        
        # Get the last bot response to check for suggested questions
        last_bot_message = None
        for msg in reversed(st.session_state.conversation_history):
            if msg["role"] == "assistant":
                last_bot_message = msg
                break
        
        if last_bot_message:
            # Simple suggested questions based on current context
            if st.session_state.language == "he":
                suggested_questions = [
                    "איזה שירותי שיניים זמינים עבורי?",
                    "מה ההטבות שלי ברמת הביטוח הנוכחית?",
                    "איך אני יכול לקבוע תור?",
                    "מה ההבדל בין הרמות השונות של הביטוח?"
                ]
            else:
                suggested_questions = [
                    "What dental services are available for me?",
                    "What are my benefits at my current insurance level?",
                    "How can I schedule an appointment?",
                    "What's the difference between the different insurance levels?"
                ]
            
            st.markdown(f"### {get_text('suggested_questions')}")
            cols = st.columns(2)
            for i, question in enumerate(suggested_questions):
                col_idx = i % 2
                if cols[col_idx].button(question, key=f"suggested_{i}"):
                    # Instead of modifying user_input, add the question directly to conversation
                    add_message_to_history("user", question)
                    # Input will automatically clear due to dynamic key change
                    
                    # Send the suggested question to the API with better visual feedback
                    with st.spinner(f"🤖 {get_text('loading')}..."):
                        response = send_chat_message(question)
                    
                    if response:
                        # Add bot response to history
                        add_message_to_history("assistant", response["response"])
                        
                        # Update phase if needed (internal logic only)
                        if response["phase"] != st.session_state.current_phase:
                            st.session_state.current_phase = response["phase"]
                            if response["phase"] == "qa":
                                st.success(get_text("user_info_collected"))
                        
                        # Update user info completion status
                        st.session_state.user_info_complete = response["user_info_complete"]
                        
                        # Store user_info if provided (important for QA phase)
                        if "user_info" in response and response["user_info"]:
                            st.session_state.user_info = response["user_info"]
                        
                        # Rerun to show the new conversation
                        st.rerun()

if __name__ == "__main__":
    main()
