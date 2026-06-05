import streamlit as st
import textwrap
import base64
import yaml
import os

def get_custom_css():
    """Return custom CSS for modern white + blue theme."""
    css_content = """
    <style>
        /* ===== GLOBAL RESET & FONT ===== */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
        
        html, body, [class*="css"] {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        }
        
        /* ===== MAIN APP ===== */
        .stApp {
            background: #FAFBFC;
        }
        
        /* ===== HEADER ===== */
        .app-header {
            background: linear-gradient(135deg, #1565C0 0%, #1976D2 50%, #1E88E5 100%);
            padding: 1.5rem 2rem;
            border-radius: 0 0 20px 20px;
            margin: -3rem -4rem 2rem -4rem;
            text-align: center;
            box-shadow: 0 4px 20px rgba(21, 101, 192, 0.25);
        }
        .app-header h1 {
            color: white !important;
            font-weight: 700;
            font-size: 1.75rem;
            margin: 0;
            letter-spacing: -0.5px;
        }
        .app-header p {
            color: rgba(255,255,255,0.85);
            font-size: 0.9rem;
            margin: 0.35rem 0 0 0;
            font-weight: 300;
        }
        
        /* ===== CHAT MESSAGES ===== */
        /* User message bubble — old & new Streamlit selectors */
        div[data-testid="chatMessage"] div[data-testid="chatAvatarIcon-user"],
        div[data-testid="stChatMessageAvatarUser"] {
            background: #1976D2 !important;
            border-radius: 50% !important;
        }
        /* Replace "face" icon → "person" via pseudo-element */
        div[data-testid="stChatMessageAvatarUser"] span[data-testid="stIconMaterial"] {
            font-size: 0 !important;
            color: transparent !important;
        }
        div[data-testid="stChatMessageAvatarUser"] span[data-testid="stIconMaterial"]::before {
            content: "person";
            font-family: 'Material Symbols Outlined', 'Material Icons', sans-serif;
            font-size: 20px !important;
            color: white !important;
            display: block;
            font-style: normal;
            font-weight: normal;
            speak: never;
            -webkit-font-smoothing: antialiased;
        }
        div[data-testid="chatMessage"]:has(div[data-testid="chatAvatarIcon-user"]),
        div[data-testid="stChatMessage"]:has(div[data-testid="stChatMessageAvatarUser"]) {
            background: #E3F2FD;
            border-radius: 18px 18px 4px 18px;
            padding: 0.75rem 1rem;
            margin: 0.5rem 0;
            border: 1px solid rgba(25, 118, 210, 0.12);
        }
        
        /* AI message bubble — old & new Streamlit selectors */
        div[data-testid="chatMessage"] div[data-testid="chatAvatarIcon-assistant"],
        div[data-testid="stChatMessageAvatarAssistant"] {
            background: #1565C0 !important;
            border-radius: 50% !important;
        }
        div[data-testid="chatMessage"]:has(div[data-testid="chatAvatarIcon-assistant"]),
        div[data-testid="stChatMessage"]:has(div[data-testid="stChatMessageAvatarAssistant"]) {
            background: white;
            border-radius: 18px 18px 18px 4px;
            padding: 0.75rem 1rem;
            margin: 0.5rem 0;
            border: 1px solid #E0E0E0;
            box-shadow: 0 1px 4px rgba(0,0,0,0.04);
        }
        
        /* ===== CHAT INPUT ===== */
        div[data-testid="stChatInput"] {
            border: 2px solid #E0E0E0 !important;
            border-radius: 16px !important;
            padding: 0.35rem 0.35rem 0.35rem 1rem !important;
            background: white !important;
            box-shadow: 0 2px 8px rgba(0,0,0,0.04) !important;
            transition: all 0.2s ease;
        }
        div[data-testid="stChatInput"]:focus-within {
            border-color: #1976D2 !important;
            box-shadow: 0 2px 12px rgba(25, 118, 210, 0.15) !important;
        }
        div[data-testid="stChatInput"] button {
            background: #1976D2 !important;
            border-radius: 12px !important;
            color: white !important;
            padding: 0.35rem 0.75rem !important;
        }
        div[data-testid="stChatInput"] button:hover {
            background: #1565C0 !important;
        }
        
        /* ===== SIDEBAR ===== */
        section[data-testid="stSidebar"] {
            background: linear-gradient(180deg, #FAFBFC 0%, #F5F7FA 100%);
            border-right: 1px solid #E8ECF0;
        }
        section[data-testid="stSidebar"] .stMarkdown {
            font-family: 'Inter', sans-serif;
        }
        
        /* Sidebar card */
        .sidebar-card {
            background: white;
            border-radius: 16px;
            padding: 1.5rem;
            margin-bottom: 1rem;
            border: 1px solid #E8ECF0;
            box-shadow: 0 2px 8px rgba(0,0,0,0.04);
        }
        .sidebar-card h3 {
            color: #1565C0;
            font-weight: 600;
            font-size: 1rem;
            margin: 0 0 1rem 0;
            padding-bottom: 0.75rem;
            border-bottom: 2px solid #E3F2FD;
        }
        
        /* Sidebar button */
        div[data-testid="stSidebar"] div.stButton button {
            background: white !important;
            border: 2px solid #1976D2 !important;
            color: #1976D2 !important;
            border-radius: 12px !important;
            font-weight: 600 !important;
            font-size: 0.85rem !important;
            padding: 0.5rem 1rem !important;
            transition: all 0.2s ease !important;
            font-family: 'Inter', sans-serif !important;
        }
        div[data-testid="stSidebar"] div.stButton button:hover {
            background: #1976D2 !important;
            color: white !important;
            box-shadow: 0 4px 12px rgba(25, 118, 210, 0.3) !important;
        }
        
        /* Sidebar info box */
        div[data-testid="stSidebar"] div[data-testid="stInfo"] {
            background: #E3F2FD;
            border: 1px solid rgba(25, 118, 210, 0.15);
            border-radius: 12px;
            padding: 1rem;
            font-family: 'Courier New', monospace;
            font-size: 0.8rem;
            color: #1565C0;
        }
        
        /* ===== STATUS / INTERMEDIATE STEPS ===== */
        div[data-testid="stStatusWidget"] {
            background: #F5F7FA;
            border-radius: 12px;
            border: 1px solid #E8ECF0;
            padding: 0.5rem;
            margin: 0.5rem 0;
        }
        
        /* ===== SCROLLBAR ===== */
        ::-webkit-scrollbar {
            width: 6px;
        }
        ::-webkit-scrollbar-track {
            background: transparent;
        }
        ::-webkit-scrollbar-thumb {
            background: #B0BEC5;
            border-radius: 3px;
        }
        ::-webkit-scrollbar-thumb:hover {
            background: #78909C;
        }
    </style>
    """
    return "\n".join([line.strip() for line in css_content.split("\n")])


def get_saas_sidebar_css():
    """Return custom CSS for modern SAAS-style sidebar with glassmorphism."""
    css_content = """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200');

        /* ===== MATERIAL SYMBOLS OUTLINED ICON SYSTEM ===== */
        .material-symbols-outlined {
            font-family: 'Material Symbols Outlined';
            font-weight: normal;
            font-style: normal;
            font-size: 20px;
            line-height: 1;
            letter-spacing: normal;
            text-transform: none;
            display: inline-block;
            white-space: nowrap;
            word-wrap: normal;
            direction: ltr;
            -webkit-font-feature-settings: 'liga';
            -webkit-font-smoothing: antialiased;
            vertical-align: middle;
        }

        /* ===== SAAS SIDEBAR CSS VARIABLES ===== */
        :root {
            --primary-600: #1565C0;
            --primary-500: #1976D2;
            --primary-400: #1E88E5;
            --primary-100: #E3F2FD;
            --primary-50: #F5F9FF;
            --text-primary: #1A1A2E;
            --text-secondary: #5A5D72;
            --text-muted: #9A9DAF;
            --surface-hover: #F0F4F8;
            --surface-active: #E3F2FD;
            --border-light: #E8ECF0;
            --border-medium: #D0D5DD;
            --success: #10B981;
            --warning: #F59E0B;
            --danger: #EF4444;
            --sidebar-width: 270px;
            --sidebar-collapsed-width: 60px;
        }

        /* ===== OVERRIDE STREAMLIT SIDEBAR ===== */
        section[data-testid="stSidebar"] {
            background: rgba(255, 255, 255, 0.85) !important;
            backdrop-filter: blur(20px) !important;
            -webkit-backdrop-filter: blur(20px) !important;
            border-right: 1px solid rgba(255, 255, 255, 0.25) !important;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.08) !important;
            transition: width 300ms cubic-bezier(0.4, 0, 0.2, 1) !important;
            overflow-x: hidden !important;
            z-index: 100 !important;
        }

        /* Hide ugly Streamlit native collapse button */
        button[data-testid="baseButton-header"] {
            display: none !important;
        }

        /* Remove default sidebar padding */
        section[data-testid="stSidebar"] > div:first-child {
            padding-top: 0 !important;
            padding-bottom: 0 !important;
        }

        /* ===== SAAS SIDEBAR CONTAINER ===== */
        .saas-sidebar {
            display: flex;
            flex-direction: column;
            height: 100vh;
            padding: 16px 0;
            gap: 4px;
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        }

        /* ===== BRAND SECTION ===== */
        .saas-sidebar__brand {
            display: flex;
            flex-direction: column;
            align-items: center;
            padding: 8px 16px 16px 16px;
            gap: 6px;
            flex-shrink: 0;
        }
        .saas-sidebar__brand-logo-wrap {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            gap: 12px;
            width: 100%;
        }
        .saas-sidebar__brand-logo {
            width: 100px;
            height: auto;
            border-radius: 8px;
            flex-shrink: 0;
            transition: all 0.2s ease;
        }
        .saas-sidebar__brand-logo:hover {
            transform: scale(1.05);
        }
        .saas-sidebar__brand-name {
            font-weight: 700;
            font-size: 1rem;
            color: var(--text-primary);
            white-space: nowrap;
            overflow: hidden;
            letter-spacing: -0.3px;
        }
        .saas-sidebar__brand-status {
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 6px;
            font-size: 0.7rem;
            color: var(--text-muted);
            white-space: nowrap;
        }
        .saas-sidebar__brand-status::before {
            content: '';
            display: inline-block;
            width: 6px;
            height: 6px;
            background: var(--success);
            border-radius: 50%;
            animation: saas-pulse 2s ease-in-out infinite;
        }

        /* ===== NAVIGATION MENU ===== */
        .saas-sidebar__nav {
            display: flex;
            flex-direction: column;
            gap: 2px;
            padding: 4px 8px;
            flex-shrink: 0;
        }
        .saas-sidebar__nav-item {
            display: flex;
            align-items: center;
            gap: 12px;
            padding: 8px 12px;
            border-radius: 8px;
            cursor: pointer;
            color: var(--text-secondary);
            font-size: 0.85rem;
            font-weight: 500;
            transition: background 200ms ease, color 200ms ease, box-shadow 200ms ease;
            border-left: 3px solid transparent;
            user-select: none;
            text-decoration: none;
            white-space: nowrap;
        }
        .saas-sidebar__nav-item:hover {
            background: var(--surface-hover);
            color: var(--text-primary);
        }
        .saas-sidebar__nav-item--active {
            background: var(--surface-active) !important;
            color: var(--primary-600) !important;
            font-weight: 600;
            box-shadow: 0 0 12px rgba(21, 101, 192, 0.12);
            position: relative;
        }
        .saas-sidebar__nav-item--active::before {
            content: '';
            position: absolute;
            left: -3px;
            top: 4px;
            bottom: 4px;
            width: 3px;
            background: linear-gradient(180deg, #1565C0, #1E88E5);
            border-radius: 0 3px 3px 0;
        }
        .saas-sidebar__nav-icon {
            font-size: 20px;
            width: 24px;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            flex-shrink: 0;
            line-height: 1;
        }
        .saas-sidebar__nav-label {
            font-size: 0.85rem;
            white-space: nowrap;
        }

        /* ===== DIVIDER ===== */
        .saas-sidebar__divider {
            height: 1px;
            background: var(--border-light);
            margin: 8px 16px;
            flex-shrink: 0;
        }

        /* ===== CTF CHALLENGE SECTION ===== */
        .saas-sidebar__ctf {
            padding: 4px 8px;
            flex-shrink: 0;
        }
        .saas-sidebar__ctf-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            cursor: pointer;
            padding: 8px 12px;
            font-weight: 600;
            font-size: 0.78rem;
            color: var(--text-primary);
            border-radius: 8px;
            transition: background 200ms ease;
            user-select: none;
        }
        .saas-sidebar__ctf-header:hover {
            background: var(--surface-hover);
        }
        .saas-sidebar__ctf-chevron {
            font-size: 0.65rem;
            transition: transform 300ms ease;
            color: var(--text-muted);
        }
        .saas-sidebar__ctf-chevron--open {
            transform: rotate(180deg);
        }
        .saas-sidebar__ctf-content {
            max-height: 400px;
            overflow: hidden;
            transition: max-height 300ms ease, opacity 250ms ease, padding 250ms ease;
            opacity: 1;
            padding: 8px 12px;
        }
        .saas-sidebar__ctf-content--collapsed {
            max-height: 0 !important;
            opacity: 0;
            padding: 0 12px;
        }
        .saas-sidebar__ctf-desc {
            font-size: 0.78rem;
            color: var(--text-secondary);
            line-height: 1.5;
            margin-bottom: 10px;
        }
        .saas-sidebar__flag-item {
            display: flex;
            align-items: center;
            gap: 8px;
            padding: 6px 8px;
            border-radius: 6px;
            font-size: 0.78rem;
            color: var(--text-secondary);
            margin-bottom: 4px;
            background: var(--primary-50);
            transition: background 200ms ease;
        }
        .saas-sidebar__flag-item:hover {
            background: var(--primary-100);
        }
        .saas-sidebar__flag-icon {
            font-size: 18px;
            flex-shrink: 0;
            display: inline-flex;
            align-items: center;
            justify-content: center;
        }
        .saas-sidebar__flag-icon--completed {
            color: var(--success);
        }
        .saas-sidebar__flag-icon--locked {
            color: var(--text-muted);
        }
        .saas-sidebar__flag-label {
            font-weight: 600;
            color: var(--text-primary);
            margin-right: 4px;
        }
        .saas-sidebar__schema-btn {
            width: 100%;
            margin-top: 8px;
            padding: 6px 12px;
            border: 1.5px solid var(--primary-400);
            border-radius: 8px;
            background: white;
            color: var(--primary-600);
            font-size: 0.75rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 200ms ease;
            font-family: 'Inter', sans-serif;
        }
        .saas-sidebar__schema-btn:hover {
            background: var(--primary-600);
            color: white;
            box-shadow: 0 2px 8px rgba(21, 101, 192, 0.25);
        }
        .saas-sidebar__schema-box {
            margin-top: 8px;
            background: var(--primary-50);
            border: 1px solid var(--primary-100);
            border-radius: 8px;
            padding: 10px;
            font-family: 'Courier New', monospace;
            font-size: 0.72rem;
            color: var(--primary-600);
            line-height: 1.6;
        }
        .saas-sidebar__ext-links {
            margin-top: 10px;
            font-size: 0.72rem;
            display: flex;
            flex-direction: column;
            gap: 4px;
        }
        .saas-sidebar__ext-links a {
            color: var(--primary-500);
            text-decoration: none;
            transition: color 200ms ease;
        }
        .saas-sidebar__ext-links a:hover {
            color: var(--primary-600);
            text-decoration: underline;
        }

        /* ===== USER PROFILE SECTION ===== */
        .saas-sidebar__spacer {
            flex: 1;
            min-height: 8px;
        }
        .saas-sidebar__user {
            display: flex;
            align-items: center;
            gap: 10px;
            padding: 12px 16px;
            border-top: 1px solid var(--border-light);
            margin-top: auto;
            flex-shrink: 0;
        }
        .saas-sidebar__user-avatar {
            width: 36px;
            height: 36px;
            border-radius: 10px;
            background: linear-gradient(135deg, #1565C0, #1E88E5);
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: 700;
            font-size: 0.85rem;
            flex-shrink: 0;
            position: relative;
        }
        .saas-sidebar__user-status-dot {
            position: absolute;
            bottom: 1px;
            right: 1px;
            width: 10px;
            height: 10px;
            background: var(--success);
            border: 2px solid white;
            border-radius: 50%;
        }
        .saas-sidebar__user-info {
            display: flex;
            flex-direction: column;
            flex: 1;
            min-width: 0;
        }
        .saas-sidebar__user-name {
            font-weight: 600;
            font-size: 0.82rem;
            color: var(--text-primary);
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }
        .saas-sidebar__user-badge {
            font-size: 0.7rem;
            color: var(--text-muted);
        }
        .saas-sidebar__user-actions {
            display: flex;
            gap: 4px;
            flex-shrink: 0;
        }
        .saas-sidebar__user-action-btn {
            width: 28px;
            height: 28px;
            border-radius: 6px;
            border: none;
            background: transparent;
            cursor: pointer;
            font-size: 0.9rem;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: background 200ms ease;
            color: var(--text-muted);
        }
        .saas-sidebar__user-action-btn:hover {
            background: var(--surface-hover);
            color: var(--text-secondary);
        }

        /* ===== COLLAPSE TOGGLE ===== */
        .saas-sidebar__toggle-wrap {
            display: flex;
            align-items: center;
            justify-content: flex-end;
            padding: 4px 12px;
            flex-shrink: 0;
        }
        .saas-sidebar__toggle {
            width: 28px;
            height: 28px;
            border-radius: 6px;
            border: 1px solid var(--border-light);
            background: white;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: all 200ms ease;
            color: var(--text-secondary);
            box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        }
        .saas-sidebar__toggle:hover {
            background: var(--surface-hover);
            color: var(--text-primary);
            border-color: var(--border-medium);
            box-shadow: 0 2px 6px rgba(0,0,0,0.08);
        }
        .saas-sidebar__toggle .material-symbols-outlined {
            font-size: 18px;
        }

        /* ===== COLLAPSED STATE OVERRIDES ===== */
        .saas-sidebar--collapsed .saas-sidebar__brand-name,
        .saas-sidebar--collapsed .saas-sidebar__brand-status,
        .saas-sidebar--collapsed .saas-sidebar__nav-label,
        .saas-sidebar--collapsed .saas-sidebar__ctf,
        .saas-sidebar--collapsed .saas-sidebar__user-info,
        .saas-sidebar--collapsed .saas-sidebar__user-actions,
        .saas-sidebar--collapsed .saas-sidebar__divider,
        .saas-sidebar--collapsed .saas-sidebar__toggle-wrap {
            opacity: 0;
            visibility: hidden;
            width: 0;
            height: 0;
            overflow: hidden;
            margin: 0;
            padding: 0;
            transition: opacity 150ms ease, visibility 150ms ease;
        }

        .saas-sidebar--collapsed .saas-sidebar__brand {
            padding: 8px 0;
            align-items: center;
        }
        .saas-sidebar--collapsed .saas-sidebar__brand-logo-wrap {
            justify-content: center;
        }
        .saas-sidebar--collapsed .saas-sidebar__brand-logo {
            width: 32px;
            height: 32px;
        }
        .saas-sidebar--collapsed .saas-sidebar__nav-item {
            justify-content: center;
            padding: 8px 0;
            border-left: 3px solid transparent;
        }
        .saas-sidebar--collapsed .saas-sidebar__nav-item--active::before {
            left: 0;
        }
        .saas-sidebar--collapsed .saas-sidebar__nav-icon {
            font-size: 1.2rem;
        }
        .saas-sidebar--collapsed .saas-sidebar__user {
            justify-content: center;
            padding: 12px 0;
        }

        /* Expanded state: show labels with slight delay */
        .saas-sidebar:not(.saas-sidebar--collapsed) .saas-sidebar__brand-name,
        .saas-sidebar:not(.saas-sidebar--collapsed) .saas-sidebar__brand-status,
        .saas-sidebar:not(.saas-sidebar--collapsed) .saas-sidebar__nav-label,
        .saas-sidebar:not(.saas-sidebar--collapsed) .saas-sidebar__user-info,
        .saas-sidebar:not(.saas-sidebar--collapsed) .saas-sidebar__user-actions {
            opacity: 1;
            visibility: visible;
            transition: opacity 200ms ease 100ms, visibility 200ms ease 100ms;
        }

        /* ===== KEYFRAME ANIMATIONS ===== */
        @keyframes saas-pulse {
            0%, 100% { opacity: 1; box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.4); }
            50% { opacity: 0.8; box-shadow: 0 0 0 4px rgba(16, 185, 129, 0); }
        }
        @keyframes saas-fadeIn {
            from { opacity: 0; transform: translateY(-4px); }
            to { opacity: 1; transform: translateY(0); }
        }
        @keyframes saas-slideDown {
            from { max-height: 0; opacity: 0; }
            to { max-height: 400px; opacity: 1; }
        }

        /* ===== TOOLTIP FOR COLLAPSED NAV ITEMS ===== */
        .saas-sidebar--collapsed .saas-sidebar__nav-item {
            position: relative;
        }
        .saas-sidebar--collapsed .saas-sidebar__nav-item:hover::after {
            content: attr(data-tooltip);
            position: absolute;
            left: calc(100% + 12px);
            top: 50%;
            transform: translateY(-50%);
            background: var(--text-primary);
            color: white;
            padding: 4px 10px;
            border-radius: 6px;
            font-size: 0.75rem;
            font-weight: 500;
            white-space: nowrap;
            z-index: 200;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            pointer-events: none;
        }

        /* ===== SCROLLBAR ===== */
        section[data-testid="stSidebar"]::-webkit-scrollbar {
            width: 3px;
        }
        section[data-testid="stSidebar"]::-webkit-scrollbar-track {
            background: transparent;
        }
        section[data-testid="stSidebar"]::-webkit-scrollbar-thumb {
            background: rgba(0, 0, 0, 0.1);
            border-radius: 2px;
        }
        section[data-testid="stSidebar"]::-webkit-scrollbar-thumb:hover {
            background: rgba(0, 0, 0, 0.2);
        }

        /* ===== HIDE STATE-BRIDGE BUTTONS ===== */
        /* Invisible Streamlit buttons used as JS → session_state bridges.
           These must remain in the DOM for JS click bridging, but hidden from view. */
        section[data-testid="stSidebar"] div[data-testid="stButton"] {
            display: none !important;
        }
    </style>
    """
    return "\n".join([line.strip() for line in css_content.split("\n")])





def get_image_base64(path):
    """Convert image to base64 for HTML embedding."""
    with open(path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode()
    return encoded_string





def render_saas_sidebar():
    """Render the modern SAAS-style sidebar.
    
    Pattern: Visual HTML rendered via markdown for all UI elements.
    Invisible Streamlit buttons rendered after for state persistence.
    JS onclick bridges: HTML element clicks → trigger hidden Streamlit buttons.
    CTF section uses pure JS for cosmetic toggle/schema (no state needed).
    """
    st.sidebar.markdown(get_saas_sidebar_css(), unsafe_allow_html=True)
    
    logo_base64 = get_image_base64("assets/labs-logo.png")
    collapsed = st.session_state.get("saas_sidebar_collapsed", False)
    
    sidebar_class = "saas-sidebar--collapsed" if collapsed else "saas-sidebar"
    
    flag1_status = st.session_state.get("saas_flags_status", {}).get("flag1", "locked")
    flag2_status = st.session_state.get("saas_flags_status", {}).get("flag2", "locked")
    flag1_icon = "check_circle" if flag1_status == "completed" else "lock"
    flag2_icon = "check_circle" if flag2_status == "completed" else "lock"
    
    flag1_class = "saas-sidebar__flag-icon--completed" if flag1_status == "completed" else "saas-sidebar__flag-icon--locked"
    flag2_class = "saas-sidebar__flag-icon--completed" if flag2_status == "completed" else "saas-sidebar__flag-icon--locked"
    
    # Build the full visual sidebar HTML
    visual_html = f"""
    <div class="{sidebar_class}" id="saas-sidebar-root">
        <!-- Toggle Button -->
  
        
        <!-- Brand Section -->
        <div class="saas-sidebar__brand">
            <div class="saas-sidebar__brand-logo-wrap">
                <img class="saas-sidebar__brand-logo" src="data:image/png;base64,{logo_base64}" alt="Logo">
                <span class="saas-sidebar__brand-name">Chatbot LLM Agent</span>
            </div>
            <span class="saas-sidebar__brand-status">System Online</span>
        </div>
        
        <!-- Divider -->
        <div class="saas-sidebar__divider"></div>
        
        <!-- CTF Challenge Section -->
        <div class="saas-sidebar__ctf">
            <div class="saas-sidebar__ctf-header" onclick="
                var c = this.nextElementSibling;
                var v = this.querySelector('.saas-sidebar__ctf-chevron');
                c.classList.toggle('saas-sidebar__ctf-content--collapsed');
                v.classList.toggle('saas-sidebar__ctf-chevron--open');
            ">
                <span>Hướng dẫn khai thác</span>
                <span class="saas-sidebar__ctf-chevron saas-sidebar__ctf-chevron--open material-symbols-outlined" style="font-size:16px;">expand_more</span>
            </div>
            <div class="saas-sidebar__ctf-content">
                <div class="saas-sidebar__ctf-desc">
                    Khai thác trợ lý ReAct này thông qua <strong>prompt injection</strong>
                    để lấy <strong>hai flag</strong> từ cơ sở dữ liệu.
                </div>
                <div class="saas-sidebar__flag-item">
                    <span class="saas-sidebar__flag-icon {flag1_class}"><span class="material-symbols-outlined">{flag1_icon}</span></span>
                    <span><span class="saas-sidebar__flag-label">Flag 1:</span> Xem giao dịch của user ID 2</span>
                </div>
                <div class="saas-sidebar__flag-item">
                    <span class="saas-sidebar__flag-icon {flag2_class}"><span class="material-symbols-outlined">{flag2_icon}</span></span>
                    <span><span class="saas-sidebar__flag-label">Flag 2:</span> Lấy mật khẩu người dùng khác</span>
                </div>
                <button class="saas-sidebar__schema-btn" onclick="
                    var b = document.getElementById('saas-schema-box');
                    if (b.style.display === 'none' || b.style.display === '') {{
                        b.style.display = 'block'; this.textContent = 'Ẩn sơ đồ cơ sở dữ liệu';
                    }} else {{
                        b.style.display = 'none'; this.textContent = 'Hiện sơ đồ cơ sở dữ liệu';
                    }}
                ">Hiện sơ đồ cơ sở dữ liệu</button>
                <div class="saas-sidebar__schema-box" id="saas-schema-box" style="display:none;">
                    <strong>Users</strong>(userId, username, password)<br>
                    <strong>Transactions</strong>(transactionId, userId, reference, recipient, amount)
                </div>
                <div class="saas-sidebar__ext-links">
                    <span>Tìm hiểu:</span>
                    <a href="https://labs.withsecure.com/publications/llm-agent-prompt-injection" target="_blank" style="display:flex;align-items:center;gap:6px;"><span class="material-symbols-outlined" style="font-size:14px;">description</span> Prompt Injection</a>
                    <a href="https://youtu.be/43qfHaKh0Xk" target="_blank" style="display:flex;align-items:center;gap:6px;"><span class="material-symbols-outlined" style="font-size:14px;">play_circle</span> SQL Injection</a>
                </div>
            </div>
        </div>
    </div>
    """
    
    # Strip leading/trailing whitespaces from each line so Markdown doesn't treat indented blocks as preformatted code
    visual_html = "\n".join([line.strip() for line in visual_html.split("\n")])
    
    st.sidebar.markdown(visual_html, unsafe_allow_html=True)
    
    # ===== INVISIBLE STREAMLIT BUTTONS (state persistence bridge) =====
    # Hidden via CSS: section[data-testid="stSidebar"] div[data-testid="stButton"] { display: none !important; }
    # JS onclick in the HTML sidebar uses sibling traversal:
    #   find marker div (.saas-nav-bridge[data-idx=X]) → nextElementSibling → button → .click()
    # Marker divs are empty/invisible; they exist only as DOM anchors for the JS query.
    
    # Toggle button — collapsed state
    st.sidebar.markdown('<div class="saas-nav-bridge" data-idx="toggle"></div>', unsafe_allow_html=True)
    if st.sidebar.button("toggle", key="saas_sidebar_toggle"):
        st.session_state["saas_sidebar_collapsed"] = not st.session_state.get("saas_sidebar_collapsed", False)
        st.rerun()


def render_header():
    """Render the modern gradient header."""
    st.markdown("""
    <div class="app-header">
        <h1>Chatbot LLM Agent</h1>
        <p>Trợ lý thông minh — Tra cứu thông tin tài khoản và giao dịch</p>
    </div>
    """, unsafe_allow_html=True)


def _load_llm_config():
    with open('config/llm-config.yaml', 'r') as f:
        yaml_data = yaml.load(f, Loader=yaml.SafeLoader)
    return yaml_data


def fetch_model_config():
    chosen_model_name = os.getenv("model_name")
    if not chosen_model_name:
        return _load_llm_config().get("default_model")
    
    # If the user specifies the direct LiteLLM model identifier (contains a slash)
    if "/" in chosen_model_name:
        return chosen_model_name
        
    llm_config = _load_llm_config()
    for model_config in llm_config.get("models", []):
        if chosen_model_name == model_config.get("model_name"):
            return model_config.get("model")
            
    # Auto prepend ollama/ if Ollama host is set
    if os.getenv("OLLAMA_HOST") or os.getenv("OLLAMA_API_BASE"):
        return f"ollama/{chosen_model_name}"
        
    return chosen_model_name