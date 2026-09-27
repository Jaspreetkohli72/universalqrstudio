"""
app.py
Universal QR Code Studio
Specialized for direct 1-tap contact saving across iOS and Android,
plus support for all standard QR payload types with modern styling,
SVG/PDF/PNG exports, and live scan simulation.
"""

import streamlit as st
from PIL import Image
import os
from datetime import datetime, date, time

from qr_payloads import (
    build_vcard_3,
    build_vcard_4,
    build_mecard,
    build_wifi_payload,
    build_url_payload,
    build_email_payload,
    build_phone_payload,
    build_sms_payload,
    build_whatsapp_payload,
    build_location_payload,
    build_calendar_payload,
    build_upi_payload,
    build_social_payload,
    clean_phone_val,
)
from qr_renderer import (
    render_qr_image,
    render_qr_svg,
    generate_pdf_contact_card,
)
from presets import CONTACT_PRESETS, WIFI_PRESETS

# Page configuration
st.set_page_config(
    page_title="Universal QR Studio | Direct iOS & Android Contact Save",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom Styling (Dark Luxury Glassmorphic Design)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    /* Main background */
    .stApp {
        background: radial-gradient(circle at 15% 15%, #111827 0%, #0b0f19 50%, #030712 100%);
        color: #f3f4f6;
    }

    /* Hero Banner */
    .hero-container {
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.7) 0%, rgba(15, 23, 42, 0.85) 100%);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 16px;
        padding: 24px 30px;
        margin-bottom: 24px;
        box-shadow: 0 10px 30px -10px rgba(0, 0, 0, 0.5), inset 0 1px 0 rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(16px);
    }
    .hero-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: linear-gradient(90deg, #3b82f6, #8b5cf6);
        color: #ffffff;
        font-size: 0.75rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        padding: 4px 12px;
        border-radius: 9999px;
        margin-bottom: 12px;
    }
    .hero-title {
        font-size: 2.1rem;
        font-weight: 800;
        letter-spacing: -0.02em;
        background: linear-gradient(135deg, #ffffff 30%, #94a3b8 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0 0 8px 0;
    }
    .hero-desc {
        color: #94a3b8;
        font-size: 0.95rem;
        margin: 0;
        max-width: 800px;
        line-height: 1.5;
    }

    /* Glass card containers */
    .glass-card {
        background: rgba(17, 24, 39, 0.75);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 14px;
        padding: 20px;
        margin-bottom: 16px;
        box-shadow: 0 4px 20px -2px rgba(0, 0, 0, 0.35);
        backdrop-filter: blur(12px);
    }

    /* Simulation Preview Cards */
    .sim-card-ios {
        background: linear-gradient(145deg, #1e293b, #0f172a);
        border: 1px solid rgba(59, 130, 246, 0.3);
        border-radius: 12px;
        padding: 14px;
        margin-top: 12px;
        box-shadow: 0 4px 15px rgba(59, 130, 246, 0.1);
    }
    .sim-card-android {
        background: linear-gradient(145deg, #132a1e, #0c1a13);
        border: 1px solid rgba(16, 185, 129, 0.3);
        border-radius: 12px;
        padding: 14px;
        margin-top: 10px;
        box-shadow: 0 4px 15px rgba(16, 185, 129, 0.1);
    }
    .sim-header {
        display: flex;
        align-items: center;
        gap: 8px;
        font-size: 0.82rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 6px;
    }
    .sim-body {
        font-size: 0.88rem;
        color: #cbd5e1;
        line-height: 1.4;
    }

    /* Compatibility pill badges */
    .compat-badge {
        display: inline-flex;
        align-items: center;
        gap: 4px;
        background: rgba(34, 197, 94, 0.15);
        border: 1px solid rgba(34, 197, 94, 0.3);
        color: #4ade80;
        font-size: 0.72rem;
        font-weight: 600;
        padding: 3px 8px;
        border-radius: 6px;
        margin: 2px 4px 2px 0;
    }

    /* QR Canvas Display Wrapper */
    .qr-canvas-wrapper {
        background: linear-gradient(145deg, #1e293b, #0f172a);
        border: 1px solid rgba(255, 255, 255, 0.12);
        border-radius: 16px;
        padding: 24px;
        text-align: center;
        box-shadow: 0 12px 36px rgba(0, 0, 0, 0.45);
        margin-bottom: 20px;
    }

    /* Buttons enhancement */
    div.stButton > button {
        border-radius: 10px;
        font-weight: 600;
        transition: all 0.2s ease-in-out;
    }
    div.stDownloadButton > button {
        border-radius: 10px;
        font-weight: 600;
        background: linear-gradient(135deg, #2563eb, #1d4ed8);
        color: white;
        border: none;
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.35);
        transition: all 0.2s ease-in-out;
    }
    div.stDownloadButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 6px 16px rgba(37, 99, 235, 0.5);
    }
</style>
""", unsafe_allow_html=True)

# Top Hero Banner
st.markdown("""
<div class="hero-container">
    <div class="hero-badge">⚡ Universal QR Engine • RFC 2426 Compliant</div>
    <h1 class="hero-title">Universal QR Studio</h1>
    <p class="hero-desc">
        Generate premium, styled QR codes for all data types. Specifically optimized so scanning a contact QR code prompts 
        <strong>1-tap direct contact saving on both Apple iOS Camera and Android (Google Lens / Camera)</strong> without third-party apps.
    </p>
</div>
""", unsafe_allow_html=True)

# Sidebar: QR Type Selector
with st.sidebar:
    st.markdown("### 🎯 Choose QR Code Type")
    category = st.radio(
        "Select Category",
        options=[
            "👤 Contact Card (Universal iOS/Android)",
            "📶 Wi-Fi Network (Auto-Connect)",
            "🌐 Website / Link (URL)",
            "💬 WhatsApp Direct Chat",
            "✉️ Email Message",
            "📱 Phone Call",
            "💬 SMS Message",
            "📍 Location / GPS Maps",
            "📅 Calendar Event (iCal)",
            "💳 UPI / Digital Payment",
            "📝 Plain Text / Notes",
            "🔗 Social Media Profile",
        ],
        index=0,
        label_visibility="collapsed"
    )

    st.markdown("---")
    st.markdown("### 🎨 Styling & Design")
    
    module_style = st.selectbox(
        "Module Shape / Dots",
        options=["rounded", "circle", "square", "gapped", "horizontal_bars", "vertical_bars"],
        format_func=lambda x: {
            "rounded": "🌟 Rounded Corners",
            "circle": "🔵 Smooth Dots (Circle)",
            "square": "⬛ Classic Square",
            "gapped": "🔳 Gapped Modules",
            "horizontal_bars": "➖ Horizontal Lines",
            "vertical_bars": "┃ Vertical Lines"
        }.get(x, x),
        index=0
    )

    color_mode = st.selectbox(
        "Color Scheme",
        options=["solid", "radial_gradient", "horizontal_gradient", "square_gradient"],
        format_func=lambda x: {
            "solid": "Solid Color",
            "radial_gradient": "Radial Gradient (Center Glow)",
            "horizontal_gradient": "Horizontal Gradient",
            "square_gradient": "Square Gradient"
        }.get(x, x),
        index=0
    )

    col_c1, col_c2 = st.columns(2)
    with col_c1:
        front_color = st.color_picker("Primary Color", "#0F172A")
    with col_c2:
        if color_mode != "solid":
            front_color_2 = st.color_picker("Gradient Accent", "#2563EB")
        else:
            front_color_2 = front_color

    col_bg1, col_bg2 = st.columns(2)
    with col_bg1:
        back_color = st.color_picker("Background Color", "#FFFFFF")
    with col_bg2:
        transparent_bg = st.checkbox("Transparent BG (PNG)", value=False)

    st.markdown("---")
    st.markdown("### 🛡️ Center Logo / Icon")
    
    preset_icons = {
        "Auto (Based on Type)": "auto",
        "👤 Contact Person": "assets/contact.png",
        "📶 Wi-Fi": "assets/wifi.png",
        "💬 WhatsApp": "assets/whatsapp.png",
        "🔗 Link": "assets/link.png",
        "📞 Phone": "assets/phone.png",
        "✉️ Email": "assets/email.png",
        "📍 Location": "assets/location.png",
        "None (Clean QR)": "none",
        "📁 Upload Custom Logo": "custom",
    }
    selected_icon_choice = st.selectbox("Select Center Icon", options=list(preset_icons.keys()), index=0)

    uploaded_logo = None
    if selected_icon_choice == "📁 Upload Custom Logo":
        uploaded_file = st.file_uploader("Upload PNG/JPG logo", type=["png", "jpg", "jpeg", "webp"])
        if uploaded_file:
            try:
                uploaded_logo = Image.open(uploaded_file)
            except Exception as e:
                st.error(f"Error loading image: {e}")

    logo_scale = st.slider("Logo Scale (%)", min_value=16, max_value=26, value=22, step=1) / 100.0

    st.markdown("---")
    st.markdown("### 📐 Dimensions & Error Correction")
    box_size = st.slider("Resolution (Box Size)", min_value=6, max_value=24, value=12, step=1)
    border_size = st.slider("Quiet Zone / Border", min_value=1, max_value=6, value=3, step=1)
    error_correction = st.selectbox(
        "Error Correction Level",
        options=["H (High - 30% recovery, recommended)", "Q (Quartile - 25%)", "M (Medium - 15%)", "L (Low - 7%)"],
        index=0
    )[0]


# Main Layout: 2 Columns (Left: Configuration / Inputs, Right: Live Preview & Export)
left_col, right_col = st.columns([1.15, 0.85], gap="large")

payload_data = ""
contact_summary = {}

# ----------------- LEFT COLUMN: INPUT FORMS -----------------
with left_col:
    if "👤 Contact Card" in category:
        st.markdown("### 👤 Direct Contact Card Setup")
        st.markdown(
            "Configure contact details. This generates a standards-compliant **vCard 3.0** with strict RFC 2426 formatting "
            "so both **Apple iOS Camera** and **Android (Google Lens / Camera)** show a direct 1-tap **'Add to Contacts'** banner."
        )

        preset_choice = st.selectbox(
            "Load Quick Preset (Optional)",
            options=["-- Start from Scratch --"] + list(CONTACT_PRESETS.keys())
        )
        defaults = CONTACT_PRESETS.get(preset_choice, {})

        # Standards format selector
        format_mode = st.radio(
            "Contact Standard Format",
            options=[
                "vCard 3.0 (Recommended • Universal 1-Tap Save on iOS & Android)",
                "MECARD (Compact format for legacy/basic scanners)",
                "vCard 4.0 (RFC 6350 modern spec)"
            ],
            index=0
        )

        with st.expander("👤 1. Identity & Name", expanded=True):
            col_fn, col_ln = st.columns(2)
            with col_fn:
                first_name = st.text_input("First Name *", value=defaults.get("first_name", "Jordan"))
            with col_ln:
                last_name = st.text_input("Last Name *", value=defaults.get("last_name", "Vance"))

            col_p, col_m, col_s = st.columns(3)
            with col_p:
                prefix = st.text_input("Prefix (e.g. Dr., Prof.)", value=defaults.get("prefix", ""))
            with col_m:
                middle_name = st.text_input("Middle Name", value=defaults.get("middle_name", ""))
            with col_s:
                suffix = st.text_input("Suffix (e.g. Jr., Ph.D.)", value=defaults.get("suffix", ""))

            display_name = st.text_input(
                "Display / Formatted Name (FN) *",
                value=defaults.get("display_name", f"{first_name} {last_name}".strip()),
                help="Crucial for iOS Camera: iOS requires FN to display the interactive 'Add to Contacts' banner."
            )

        with st.expander("💼 2. Company & Job Title", expanded=True):
            col_c, col_d = st.columns(2)
            with col_c:
                company = st.text_input("Organization / Company", value=defaults.get("company", "NeuralStack AI"))
            with col_d:
                department = st.text_input("Department", value=defaults.get("department", "Executive Office"))
            title = st.text_input("Job Title / Designation", value=defaults.get("title", "Founder & CEO"))

        with st.expander("📞 3. Phone Numbers (Smart Auto-Format)", expanded=True):
            col_cntry, col_hint = st.columns([1.2, 1.8])
            with col_cntry:
                country_map = {
                    "🇮🇳 India (+91)": "IN",
                    "🇺🇸 United States (+1)": "US",
                    "🇬🇧 United Kingdom (+44)": "GB",
                    "🇨🇦 Canada (+1)": "CA",
                    "🇦🇺 Australia (+61)": "AU",
                    "🇦🇪 UAE (+971)": "AE",
                    "🇸🇬 Singapore (+65)": "SG",
                    "🇩🇪 Germany (+49)": "DE",
                    "🌐 Other / Auto-Detect": "IN",
                }
                selected_country_label = st.selectbox(
                    "Default Country Code",
                    options=list(country_map.keys()),
                    index=0,
                    help="Numbers entered without a '+' prefix will automatically use this country code."
                )
                selected_region = country_map[selected_country_label]
            with col_hint:
                st.markdown(
                    "<div style='margin-top: 24px; padding: 8px 12px; background: rgba(59, 130, 246, 0.1); "
                    "border: 1px solid rgba(59, 130, 246, 0.25); border-radius: 8px; font-size: 0.82rem; color: #93c5fd;'>"
                    "⚡ <strong>No manual formatting needed!</strong> Just type your digits (e.g. <code>9285033355</code>). "
                    "Country code and spacing are formatted automatically.</div>",
                    unsafe_allow_html=True
                )

            col_p1, col_p2 = st.columns(2)
            with col_p1:
                cell_phone_raw = st.text_input(
                    "Mobile / Cell Phone *",
                    value=defaults.get("cell_phone", "9285033355"),
                    help="Type digits (e.g. 9285033355). It is automatically formatted into international standard."
                )
                cell_phone = clean_phone_val(cell_phone_raw, selected_region)
                if cell_phone_raw.strip():
                    st.markdown(f"<div style='color: #4ade80; font-size: 0.82rem; font-weight: 600; margin-top: -8px; margin-bottom: 8px;'>✓ Auto-formatted: {cell_phone}</div>", unsafe_allow_html=True)
            with col_p2:
                work_phone_raw = st.text_input("Work Phone", value=defaults.get("work_phone", ""))
                work_phone = clean_phone_val(work_phone_raw, selected_region)
                if work_phone_raw.strip():
                    st.markdown(f"<div style='color: #4ade80; font-size: 0.82rem; font-weight: 600; margin-top: -8px; margin-bottom: 8px;'>✓ Auto-formatted: {work_phone}</div>", unsafe_allow_html=True)

            home_phone_raw = st.text_input("Home Phone", value=defaults.get("home_phone", ""))
            home_phone = clean_phone_val(home_phone_raw, selected_region)
            if home_phone_raw.strip():
                st.markdown(f"<div style='color: #4ade80; font-size: 0.82rem; font-weight: 600; margin-top: -8px; margin-bottom: 8px;'>✓ Auto-formatted: {home_phone}</div>", unsafe_allow_html=True)

        with st.expander("✉️ 4. Email & Web Addresses", expanded=True):
            col_e1, col_e2 = st.columns(2)
            with col_e1:
                work_email = st.text_input("Work Email", value=defaults.get("work_email", "megametalwork@gmail.com"))
            with col_e2:
                home_email = st.text_input("Personal Email", value=defaults.get("home_email", ""))
            
            col_u1, col_u2 = st.columns(2)
            with col_u1:
                website = st.text_input("Website URL", value=defaults.get("website", "https://www.instagram.com/megametalwork/"))
            with col_u2:
                social_url = st.text_input("LinkedIn / Social URL", value=defaults.get("social_url", "https://www.instagram.com/megametalwork/"))

        with st.expander("📍 5. Physical Address", expanded=False):
            street = st.text_input("Street Address", value=defaults.get("street", "Near Goverdhan Chowk, Old Rajendra Nagar"))
            col_city, col_state = st.columns(2)
            with col_city:
                city = st.text_input("City", value=defaults.get("city", "Raipur"))
            with col_state:
                state = st.text_input("State / Province", value=defaults.get("state", "Chhattisgarh"))
            col_zip, col_country = st.columns(2)
            with col_zip:
                postal_code = st.text_input("Postal / ZIP Code", value=defaults.get("postal_code", "492001"))
            with col_country:
                country = st.text_input("Country", value=defaults.get("country", "India"))

        with st.expander("📝 6. Additional Notes & Birthday", expanded=False):
            birthday = st.text_input("Birthday (YYYY-MM-DD)", value=defaults.get("birthday", ""))
            notes = st.text_area("Notes / Bio", value=defaults.get("notes", "Founder & CEO, Mega Metal Works"))

        contact_summary = {
            "name": display_name or f"{first_name} {last_name}".strip(),
            "job_org": f"{title} • {company}".strip(" •"),
            "phone": cell_phone or work_phone,
            "email": work_email or home_email,
            "website": website,
            "notes": notes,
        }

        if "vCard 4.0" in format_mode:
            payload_data = build_vcard_4(
                first_name=first_name, last_name=last_name, middle_name=middle_name,
                prefix=prefix, suffix=suffix, display_name=display_name,
                company=company, department=department, title=title,
                cell_phone=cell_phone, work_phone=work_phone, home_phone=home_phone,
                work_email=work_email, home_email=home_email, website=website,
                social_url=social_url, street=street, city=city, state=state,
                postal_code=postal_code, country=country, birthday=birthday, notes=notes,
                default_region=selected_region
            )
        elif "MECARD" in format_mode:
            payload_data = build_mecard(
                first_name=first_name, last_name=last_name, cell_phone=cell_phone,
                work_email=work_email, website=website, street=street,
                city=city, state=state, postal_code=postal_code, country=country, notes=notes,
                default_region=selected_region
            )
        else:
            payload_data = build_vcard_3(
                first_name=first_name, last_name=last_name, middle_name=middle_name,
                prefix=prefix, suffix=suffix, display_name=display_name,
                company=company, department=department, title=title,
                cell_phone=cell_phone, work_phone=work_phone, home_phone=home_phone,
                work_email=work_email, home_email=home_email, website=website,
                social_url=social_url, street=street, city=city, state=state,
                postal_code=postal_code, country=country, birthday=birthday, notes=notes,
                default_region=selected_region
            )

    elif "📶 Wi-Fi Network" in category:
        st.markdown("### 📶 Wi-Fi Auto-Connect Setup")
        st.markdown("Scan to automatically connect to a wireless network on both iOS and Android.")
        
        wf_preset = st.selectbox("Load Wi-Fi Preset (Optional)", ["-- Start from Scratch --"] + list(WIFI_PRESETS.keys()))
        wf_defs = WIFI_PRESETS.get(wf_preset, {})

        ssid = st.text_input("Network Name (SSID) *", value=wf_defs.get("ssid", "Studio_Guest_5G"))
        col_auth, col_hid = st.columns([2, 1])
        with col_auth:
            auth_type = st.selectbox(
                "Security Type",
                ["WPA/WPA2/WPA3", "WEP", "No Password (Open)"],
                index=0 if wf_defs.get("auth_type", "WPA") == "WPA" else (1 if wf_defs.get("auth_type") == "WEP" else 2)
            )
        with col_hid:
            hidden = st.checkbox("Hidden SSID", value=wf_defs.get("hidden", False))

        mapped_auth = "WPA"
        if "WEP" in auth_type:
            mapped_auth = "WEP"
        elif "Open" in auth_type:
            mapped_auth = "nopass"

        if mapped_auth != "nopass":
            password = st.text_input("Wi-Fi Password *", value=wf_defs.get("password", "SecureWiFiPass123!"), type="password")
        else:
            password = ""

        payload_data = build_wifi_payload(ssid=ssid, password=password, auth_type=mapped_auth, hidden=hidden)

    elif "🌐 Website / Link" in category:
        st.markdown("### 🌐 Website URL Setup")
        st.markdown("Scan to directly open any URL, webpage, portfolio, or landing page in the mobile browser.")
        url_input = st.text_input("Target URL *", value="https://google.com")
        payload_data = build_url_payload(url_input)

    elif "💬 WhatsApp Direct Chat" in category:
        st.markdown("### 💬 WhatsApp Direct Chat Setup")
        st.markdown("Scan to directly open a WhatsApp conversation with a pre-filled message without saving the number.")
        col_wa1, col_wa2 = st.columns([1.2, 2])
        with col_wa1:
            wa_country = st.selectbox(
                "Country Code",
                options=["🇮🇳 India (+91)", "🇺🇸 United States (+1)", "🇬🇧 United Kingdom (+44)", "🇦🇪 UAE (+971)", "🌐 Other / Auto"],
                index=0,
                key="wa_country"
            )
            wa_region = "IN" if "India" in wa_country else ("US" if "United States" in wa_country else ("GB" if "United Kingdom" in wa_country else ("AE" if "UAE" in wa_country else "IN")))
        with col_wa2:
            wa_phone_raw = st.text_input("Phone Number *", value="9285033355", help="Enter raw digits (e.g. 9285033355). No manual formatting needed.")
        wa_phone_clean = clean_phone_val(wa_phone_raw, wa_region)
        if wa_phone_raw.strip():
            st.markdown(f"<div style='color: #4ade80; font-size: 0.82rem; font-weight: 600; margin-top: -8px; margin-bottom: 8px;'>✓ Auto-formatted: {wa_phone_clean}</div>", unsafe_allow_html=True)
        wa_msg = st.text_area("Pre-filled Message", value="Hello! I scanned your QR code and would like to connect.")
        payload_data = build_whatsapp_payload(wa_phone_raw, wa_msg, default_region=wa_region)

    elif "✉️ Email Message" in category:
        st.markdown("### ✉️ Email Setup")
        st.markdown("Scan to immediately compose an email in the user's default email client.")
        email_to = st.text_input("Recipient Email *", value="megametalwork@gmail.com")
        email_subj = st.text_input("Email Subject", value="Inquiry from QR Scan")
        email_body = st.text_area("Message Body", value="Hi team,\n\nI scanned your QR code and wanted to reach out regarding...")
        with st.expander("Additional CC / BCC"):
            email_cc = st.text_input("CC", value="")
            email_bcc = st.text_input("BCC", value="")
        payload_data = build_email_payload(email_to, email_subj, email_body, email_cc, email_bcc)

    elif "📱 Phone Call" in category:
        st.markdown("### 📱 Phone Dial Setup")
        st.markdown("Scan to immediately prompt the phone's native dialer.")
        col_pc1, col_pc2 = st.columns([1.2, 2])
        with col_pc1:
            pc_country = st.selectbox(
                "Country Code",
                options=["🇮🇳 India (+91)", "🇺🇸 United States (+1)", "🇬🇧 United Kingdom (+44)", "🌐 Other / Auto"],
                index=0,
                key="pc_country"
            )
            pc_region = "IN" if "India" in pc_country else ("US" if "United States" in pc_country else ("GB" if "United Kingdom" in pc_country else "IN"))
        with col_pc2:
            phone_raw = st.text_input("Phone Number *", value="9285033355", help="Enter raw digits. Automatically formatted.")
        phone_clean = clean_phone_val(phone_raw, pc_region)
        if phone_raw.strip():
            st.markdown(f"<div style='color: #4ade80; font-size: 0.82rem; font-weight: 600; margin-top: -8px; margin-bottom: 8px;'>✓ Auto-formatted: {phone_clean}</div>", unsafe_allow_html=True)
        payload_data = build_phone_payload(phone_raw, default_region=pc_region)

    elif "💬 SMS Message" in category:
        st.markdown("### 💬 SMS Message Setup")
        st.markdown("Scan to open the SMS app with recipient number and drafted text.")
        col_sms1, col_sms2 = st.columns([1.2, 2])
        with col_sms1:
            sms_country = st.selectbox(
                "Country Code",
                options=["🇮🇳 India (+91)", "🇺🇸 United States (+1)", "🇬🇧 United Kingdom (+44)", "🌐 Other / Auto"],
                index=0,
                key="sms_country"
            )
            sms_region = "IN" if "India" in sms_country else ("US" if "United States" in sms_country else ("GB" if "United Kingdom" in sms_country else "IN"))
        with col_sms2:
            sms_raw = st.text_input("Recipient Phone *", value="9285033355", help="Enter raw digits.")
        sms_clean = clean_phone_val(sms_raw, sms_region)
        if sms_raw.strip():
            st.markdown(f"<div style='color: #4ade80; font-size: 0.82rem; font-weight: 600; margin-top: -8px; margin-bottom: 8px;'>✓ Auto-formatted: {sms_clean}</div>", unsafe_allow_html=True)
        sms_body = st.text_area("Draft Message", value="Hello! Please confirm my booking.")
        payload_data = build_sms_payload(sms_raw, sms_body, default_region=sms_region)

    elif "📍 Location / GPS Maps" in category:
        st.markdown("### 📍 Location / GPS Setup")
        st.markdown("Scan to open exact coordinates in Apple Maps or Google Maps.")
        col_lat, col_lon = st.columns(2)
        with col_lat:
            latitude = st.number_input("Latitude", value=37.7749, format="%.6f")
        with col_lon:
            longitude = st.number_input("Longitude", value=-122.4194, format="%.6f")
        loc_label = st.text_input("Location Name / Label", value="San Francisco Downtown")
        payload_data = build_location_payload(latitude, longitude, loc_label)

    elif "📅 Calendar Event" in category:
        st.markdown("### 📅 Calendar Event Setup")
        st.markdown("Scan to prompt 1-tap 'Add to Calendar' on Apple Calendar or Google Calendar.")
        event_title = st.text_input("Event Title *", value="Annual Product Keynote 2026")
        col_d1, col_t1 = st.columns(2)
        with col_d1:
            start_date = st.date_input("Start Date", value=date.today())
        with col_t1:
            start_time = st.time_input("Start Time", value=time(10, 0))
        
        col_d2, col_t2 = st.columns(2)
        with col_d2:
            end_date = st.date_input("End Date", value=date.today())
        with col_t2:
            end_time = st.time_input("End Time", value=time(11, 30))

        event_loc = st.text_input("Event Location / Video Link", value="Moscone Center, SF & Zoom")
        event_desc = st.text_area("Event Description", value="Live demonstration of next-generation features.")
        
        dt_start = datetime.combine(start_date, start_time)
        dt_end = datetime.combine(end_date, end_time)
        payload_data = build_calendar_payload(event_title, dt_start, dt_end, event_loc, event_desc)

    elif "💳 UPI / Digital Payment" in category:
        st.markdown("### 💳 UPI Payment Setup")
        st.markdown("Scan using Google Pay, PhonePe, Paytm, BHIM, or any UPI banking app.")
        col_vpa, col_pn = st.columns(2)
        with col_vpa:
            vpa = st.text_input("UPI ID / VPA *", value="merchant@upi")
        with col_pn:
            payee_name = st.text_input("Payee / Store Name", value="Apex Cafe & Store")
        
        col_am, col_cu = st.columns(2)
        with col_am:
            amount = st.number_input("Amount (0 for customer to enter)", min_value=0.0, value=250.0, step=10.0)
        with col_cu:
            currency = st.selectbox("Currency", ["INR"], index=0)
        
        pay_note = st.text_input("Payment Note / Bill Ref", value="Invoice #4821")
        payload_data = build_upi_payload(vpa, payee_name, amount, pay_note, currency)

    elif "📝 Plain Text / Notes" in category:
        st.markdown("### 📝 Plain Text / Raw Data Setup")
        st.markdown("Scan to display plain text, encoded secrets, serial keys, or raw notes.")
        raw_text = st.text_area("Enter Text Content *", value="Apex Security Key: 9F8A-23BC-8891-DE40", height=140)
        payload_data = raw_text

    elif "🔗 Social Media Profile" in category:
        st.markdown("### 🔗 Social Media Multi-Link Setup")
        st.markdown("Scan to directly open a specific social media profile.")
        platform = st.selectbox("Platform", ["LinkedIn", "Instagram", "X (Twitter)", "GitHub", "YouTube", "Telegram"], index=0)
        social_id = st.text_input("Username or Profile Link *", value="jordanvance")
        payload_data = build_social_payload(platform.lower().split()[0], social_id)


# ----------------- RIGHT COLUMN: LIVE PREVIEW & EXPORT -----------------
with right_col:
    st.markdown("### 📱 Live Dynamic QR Canvas")

    # Determine center logo
    logo_to_use = None
    if selected_icon_choice == "📁 Upload Custom Logo" and uploaded_logo:
        logo_to_use = uploaded_logo
    elif selected_icon_choice == "Auto (Based on Type)":
        if "Contact" in category:
            icon_file = "assets/contact.png"
        elif "Wi-Fi" in category:
            icon_file = "assets/wifi.png"
        elif "WhatsApp" in category:
            icon_file = "assets/whatsapp.png"
        elif "Website" in category or "Social" in category:
            icon_file = "assets/link.png"
        elif "Phone" in category:
            icon_file = "assets/phone.png"
        elif "Email" in category:
            icon_file = "assets/email.png"
        elif "Location" in category:
            icon_file = "assets/location.png"
        else:
            icon_file = None
        if icon_file and os.path.exists(icon_file):
            logo_to_use = Image.open(icon_file)
    elif selected_icon_choice != "None (Clean QR)":
        icon_path = preset_icons.get(selected_icon_choice)
        if icon_path and os.path.exists(icon_path):
            logo_to_use = Image.open(icon_path)

    # Render QR Code
    if payload_data.strip():
        try:
            qr_image, png_bytes = render_qr_image(
                payload=payload_data,
                box_size=box_size,
                border=border_size,
                error_correction=error_correction,
                module_style=module_style,
                color_mode=color_mode,
                front_color_hex=front_color,
                front_color_2_hex=front_color_2,
                back_color_hex=back_color,
                transparent_bg=transparent_bg,
                logo_img=logo_to_use,
                logo_scale=logo_scale,
            )

            # Display QR image centered
            st.image(qr_image, use_container_width=True)

            # Mobile OS Scanner Simulation & Compatibility verification
            if "👤 Contact Card" in category:
                c_name = contact_summary.get("name") or "Contact"
                c_phone = contact_summary.get("phone") or "No phone"
                c_org = contact_summary.get("job_org") or ""

                st.markdown(f"""
                <div class="sim-card-ios">
                    <div class="sim-header" style="color: #60a5fa;">
                        <span></span> Apple iPhone (iOS Camera)
                    </div>
                    <div class="sim-body">
                        <strong>Yellow Banner Prompt:</strong> "Add {c_name} to Contacts"<br>
                        <em>Tapping immediately opens native iOS Contacts sheet with name, {c_phone}, email, and address prefilled.</em>
                    </div>
                </div>

                <div class="sim-card-android">
                    <div class="sim-header" style="color: #34d399;">
                        <span>🤖</span> Android (Google Lens / Camera)
                    </div>
                    <div class="sim-body">
                        <strong>Action Chip:</strong> "Add contact" • <strong>{c_name}</strong><br>
                        <em>Tapping directly prompts 1-tap save into Google Contacts or Device Contacts.</em>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                st.markdown("<div style='margin-top: 10px;'>", unsafe_allow_html=True)
                st.markdown("<span class='compat-badge'>✓ RFC 2426 vCard 3.0</span>", unsafe_allow_html=True)
                st.markdown("<span class='compat-badge'>✓ Mandatory FN Formatted Name</span>", unsafe_allow_html=True)
                st.markdown("<span class='compat-badge'>✓ Structured N Field</span>", unsafe_allow_html=True)
                st.markdown("<span class='compat-badge'>✓ High-Res Error Correction</span>", unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)

            elif "📶 Wi-Fi" in category:
                st.markdown("""
                <div class="sim-card-ios">
                    <div class="sim-header" style="color: #60a5fa;"><span></span> iOS Camera</div>
                    <div class="sim-body">Displays <strong>"Join '[SSID]' Network"</strong> prompt. 1-tap auto-connects.</div>
                </div>
                <div class="sim-card-android">
                    <div class="sim-header" style="color: #34d399;"><span>🤖</span> Android Camera</div>
                    <div class="sim-body">Displays <strong>"Connect to [SSID]"</strong>. Auto-configures Wi-Fi without entering password.</div>
                </div>
                """, unsafe_allow_html=True)

            # Export Center
            st.markdown("### 📥 Download & Export Center")
            
            # Row 1: PNG and SVG
            c_dl1, c_dl2 = st.columns(2)
            with c_dl1:
                st.download_button(
                    label="💾 Download PNG (300 DPI)",
                    data=png_bytes,
                    file_name="universal_qr.png",
                    mime="image/png",
                    use_container_width=True
                )
            with c_dl2:
                svg_data = render_qr_svg(
                    payload=payload_data,
                    box_size=box_size,
                    border=border_size,
                    error_correction=error_correction,
                    front_color_hex=front_color,
                    back_color_hex=back_color
                )
                st.download_button(
                    label="📐 Download Vector SVG",
                    data=svg_data,
                    file_name="universal_qr.svg",
                    mime="image/svg+xml",
                    use_container_width=True
                )

            # Row 2: VCF and PDF (if Contact Card)
            if "👤 Contact Card" in category:
                c_dl3, c_dl4 = st.columns(2)
                with c_dl3:
                    st.download_button(
                        label="📇 Download .VCF File",
                        data=payload_data.encode("utf-8"),
                        file_name=f"{contact_summary.get('name', 'contact').replace(' ', '_').lower()}.vcf",
                        mime="text/vcard",
                        use_container_width=True
                    )
                with c_dl4:
                    try:
                        pdf_data = generate_pdf_contact_card(
                            qr_img=qr_image,
                            title_text="Scan to Save Contact",
                            contact_name=contact_summary.get("name", ""),
                            job_org=contact_summary.get("job_org", ""),
                            phone=contact_summary.get("phone", ""),
                            email=contact_summary.get("email", ""),
                            website=contact_summary.get("website", ""),
                            note=contact_summary.get("notes", "")
                        )
                        st.download_button(
                            label="📄 Printable Badge (PDF)",
                            data=pdf_data,
                            file_name=f"contact_badge_{contact_summary.get('name', 'contact').replace(' ', '_').lower()}.pdf",
                            mime="application/pdf",
                            use_container_width=True
                        )
                    except Exception as e:
                        st.warning(f"PDF generation note: {e}")

            # Raw Payload Inspector
            with st.expander("🔍 Inspect Raw QR Payload Data"):
                st.code(payload_data, language="text")

        except Exception as e:
            st.error(f"Error generating QR Code: {e}")
    else:
        st.info("Fill in the fields on the left to generate your QR code.")
