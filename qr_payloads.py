"""
qr_payloads.py
Encodes data payloads for all QR code types, optimized for universal compatibility.
Special focus on universal iOS and Android 1-tap contact saving.
"""

import urllib.parse
from datetime import datetime


def escape_vcard_val(val: str) -> str:
    """Escapes special characters in vCard text fields per RFC 2426."""
    if not val:
        return ""
    # Semicolon and backslash must be escaped; commas are safe in text fields and avoid ugly backslashes in phone contacts
    res = val.replace('\\', '\\\\').replace(';', '\\;')
    res = res.replace('\r\n', '\\n').replace('\n', '\\n')
    return res.strip()


def clean_phone_val(val: str, default_region: str = "IN") -> str:
    """
    Cleans and automatically formats phone number values using Google's libphonenumber.
    Features:
    - User does not need to manually format: handles raw digits (e.g. 9285033355),
      local zeros (09285033355), or international numbers (+919285033355).
    - Automatically strips any accidental 'tel:' or 'TEL:' prefixes.
    - Formats to international standard (+91 92850 33355) so both iOS & Android
      contact apps save a clean, dialable phone number.
    """
    if not val:
        return ""
    s = val.strip()
    if s.lower().startswith("tel:"):
        s = s[4:].strip()

    try:
        import phonenumbers
        # If number begins with '+', parse internationally
        if s.startswith("+"):
            parsed = phonenumbers.parse(s, None)
        else:
            parsed = phonenumbers.parse(s, default_region)
        if phonenumbers.is_possible_number(parsed):
            return phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.INTERNATIONAL)
    except Exception:
        pass

    return " ".join(s.split())


def build_vcard_3(
    first_name: str = "",
    last_name: str = "",
    middle_name: str = "",
    prefix: str = "",
    suffix: str = "",
    display_name: str = "",
    company: str = "",
    department: str = "",
    title: str = "",
    cell_phone: str = "",
    work_phone: str = "",
    home_phone: str = "",
    work_email: str = "",
    home_email: str = "",
    website: str = "",
    social_url: str = "",
    street: str = "",
    city: str = "",
    state: str = "",
    postal_code: str = "",
    country: str = "",
    birthday: str = "",
    notes: str = "",
    default_region: str = "IN",
) -> str:
    """
    Constructs a standards-compliant vCard 3.0 (RFC 2426).
    This format is universally parsed by both Apple iOS Camera and Android
    (Google Lens, Samsung Camera, Google Contacts) to trigger a direct
    'Add to Contacts' native prompt.
    """
    first_name = first_name.strip()
    last_name = last_name.strip()
    middle_name = middle_name.strip()
    prefix = prefix.strip()
    suffix = suffix.strip()

    # Formatted Name (FN) is REQUIRED by iOS Camera to show contact card banner
    if display_name.strip():
        fn = display_name.strip()
    else:
        parts = [p for p in [prefix, first_name, middle_name, last_name, suffix] if p]
        fn = " ".join(parts) if parts else "Contact"

    # Structured Name (N:LastName;FirstName;MiddleName;Prefix;Suffix)
    n_field = f"{escape_vcard_val(last_name)};{escape_vcard_val(first_name)};{escape_vcard_val(middle_name)};{escape_vcard_val(prefix)};{escape_vcard_val(suffix)}"

    lines = [
        "BEGIN:VCARD",
        "VERSION:3.0",
        f"N:{n_field}",
        f"FN:{escape_vcard_val(fn)}"
    ]

    # Organization & Department
    if company.strip() or department.strip():
        org_val = escape_vcard_val(company.strip())
        if department.strip():
            org_val += f";{escape_vcard_val(department.strip())}"
        lines.append(f"ORG:{org_val}")

    if title.strip():
        lines.append(f"TITLE:{escape_vcard_val(title.strip())}")

    # Phone numbers - clean phone value without any tel: prefix!
    if cell_phone.strip():
        lines.append(f"TEL;TYPE=CELL,VOICE:{clean_phone_val(cell_phone, default_region)}")
    if work_phone.strip():
        lines.append(f"TEL;TYPE=WORK,VOICE:{clean_phone_val(work_phone, default_region)}")
    if home_phone.strip():
        lines.append(f"TEL;TYPE=HOME,VOICE:{clean_phone_val(home_phone, default_region)}")

    # Emails
    if work_email.strip():
        lines.append(f"EMAIL;TYPE=INTERNET,WORK:{work_email.strip()}")
    if home_email.strip():
        lines.append(f"EMAIL;TYPE=INTERNET,HOME:{home_email.strip()}")

    # URLs
    if website.strip():
        lines.append(f"URL;TYPE=WORK:{website.strip()}")
    if social_url.strip():
        lines.append(f"URL;TYPE=SOCIAL:{social_url.strip()}")

    # Structured Address: ADR;TYPE=WORK:;;Street;City;State;PostalCode;Country
    addr_parts = [
        "",  # Post office box
        "",  # Extended address
        escape_vcard_val(street.strip()),
        escape_vcard_val(city.strip()),
        escape_vcard_val(state.strip()),
        escape_vcard_val(postal_code.strip()),
        escape_vcard_val(country.strip())
    ]
    if any(addr_parts[2:]):
        lines.append(f"ADR;TYPE=WORK:{';'.join(addr_parts)}")

    # Birthday (YYYY-MM-DD)
    if birthday.strip():
        lines.append(f"BDAY:{birthday.strip()}")

    # Notes
    if notes.strip():
        lines.append(f"NOTE:{escape_vcard_val(notes.strip())}")

    lines.append("END:VCARD")
    # Standard CRLF line endings for maximum RFC conformance
    return "\r\n".join(lines)


def build_vcard_4(
    first_name: str = "",
    last_name: str = "",
    middle_name: str = "",
    prefix: str = "",
    suffix: str = "",
    display_name: str = "",
    company: str = "",
    department: str = "",
    title: str = "",
    cell_phone: str = "",
    work_phone: str = "",
    home_phone: str = "",
    work_email: str = "",
    home_email: str = "",
    website: str = "",
    social_url: str = "",
    street: str = "",
    city: str = "",
    state: str = "",
    postal_code: str = "",
    country: str = "",
    birthday: str = "",
    notes: str = "",
    default_region: str = "IN",
) -> str:
    """
    Builds vCard 4.0 (RFC 6350).
    CRITICAL: Does NOT use VALUE=uri:tel: because mobile OS parsers (iOS & Android)
    literally save 'tel:+...' or 'TEL:+...' into the phone contact field!
    """
    parts = [p for p in [prefix, first_name, middle_name, last_name, suffix] if p]
    fn = display_name.strip() if display_name.strip() else (" ".join(parts) if parts else "Contact")

    n_field = f"{escape_vcard_val(last_name)};{escape_vcard_val(first_name)};{escape_vcard_val(middle_name)};{escape_vcard_val(prefix)};{escape_vcard_val(suffix)}"

    lines = [
        "BEGIN:VCARD",
        "VERSION:4.0",
        f"N:{n_field}",
        f"FN:{escape_vcard_val(fn)}"
    ]
    if company.strip() or department.strip():
        org = escape_vcard_val(company.strip())
        if department.strip():
            org += f";{escape_vcard_val(department.strip())}"
        lines.append(f"ORG:{org}")
    if title.strip():
        lines.append(f"TITLE:{escape_vcard_val(title.strip())}")
    
    # Clean phone numbers without VALUE=uri:tel: to prevent saving 'TEL:xxxx'
    if cell_phone.strip():
        lines.append(f"TEL;TYPE=cell,voice:{clean_phone_val(cell_phone, default_region)}")
    if work_phone.strip():
        lines.append(f"TEL;TYPE=work,voice:{clean_phone_val(work_phone, default_region)}")
    if home_phone.strip():
        lines.append(f"TEL;TYPE=home,voice:{clean_phone_val(home_phone, default_region)}")
        
    if work_email.strip():
        lines.append(f"EMAIL;TYPE=work:{work_email.strip()}")
    if home_email.strip():
        lines.append(f"EMAIL;TYPE=home:{home_email.strip()}")
    if website.strip():
        lines.append(f"URL;TYPE=work:{website.strip()}")
    if social_url.strip():
        lines.append(f"URL:{social_url.strip()}")
    addr_parts = [
        "", "",
        escape_vcard_val(street.strip()),
        escape_vcard_val(city.strip()),
        escape_vcard_val(state.strip()),
        escape_vcard_val(postal_code.strip()),
        escape_vcard_val(country.strip())
    ]
    if any(addr_parts[2:]):
        lines.append(f"ADR;TYPE=work:{';'.join(addr_parts)}")
    if birthday.strip():
        lines.append(f"BDAY:{birthday.strip()}")
    if notes.strip():
        lines.append(f"NOTE:{escape_vcard_val(notes.strip())}")
    lines.append("END:VCARD")
    return "\r\n".join(lines)


def build_mecard(
    first_name: str = "",
    last_name: str = "",
    cell_phone: str = "",
    work_email: str = "",
    website: str = "",
    street: str = "",
    city: str = "",
    state: str = "",
    postal_code: str = "",
    country: str = "",
    notes: str = "",
    default_region: str = "IN",
) -> str:
    """Builds NTT DoCoMo MECARD format."""
    def esc_mecard(v: str) -> str:
        return v.replace('\\', '\\\\').replace(';', '\\;').replace(':', '\\:').replace(',', '\\,')

    name = f"{last_name.strip()},{first_name.strip()}".strip(",")
    parts = ["MECARD:"]
    if name:
        parts.append(f"N:{esc_mecard(name)};")
    if cell_phone.strip():
        parts.append(f"TEL:{esc_mecard(clean_phone_val(cell_phone, default_region))};")
    if work_email.strip():
        parts.append(f"EMAIL:{esc_mecard(work_email.strip())};")
    if website.strip():
        parts.append(f"URL:{esc_mecard(website.strip())};")
    addr_parts = [p for p in [street, city, state, postal_code, country] if p.strip()]
    if addr_parts:
        parts.append(f"ADR:{esc_mecard(', '.join(addr_parts))};")
    if notes.strip():
        parts.append(f"NOTE:{esc_mecard(notes.strip())};")
    parts.append(";")
    return "".join(parts)


def build_wifi_payload(ssid: str, password: str = "", auth_type: str = "WPA", hidden: bool = False) -> str:
    """
    Constructs Wi-Fi network QR code payload.
    auth_type: 'WPA' (WPA/WPA2/WPA3), 'WEP', or 'nopass'
    """
    def esc_wifi(s: str) -> str:
        # Wi-Fi standard escapes \, ;, ,, :, "
        res = ""
        for ch in s:
            if ch in ('\\', ';', ',', ':', '"'):
                res += f"\\{ch}"
            else:
                res += ch
        return res

    auth = auth_type.upper()
    if auth not in ("WPA", "WEP", "NOPASS"):
        auth = "WPA"

    s_escaped = esc_wifi(ssid.strip())
    p_escaped = esc_wifi(password) if auth != "NOPASS" else ""
    h_flag = "true" if hidden else "false"

    return f"WIFI:S:{s_escaped};T:{auth};P:{p_escaped};H:{h_flag};;"


def build_url_payload(url: str) -> str:
    """Builds clean URL payload."""
    url = url.strip()
    if not url.startswith(("http://", "https://", "ftp://")):
        url = f"https://{url}"
    return url


def build_email_payload(to: str, subject: str = "", body: str = "", cc: str = "", bcc: str = "") -> str:
    """Builds standard mailto: URI."""
    params = {}
    if subject.strip():
        params['subject'] = subject.strip()
    if body.strip():
        params['body'] = body.strip()
    if cc.strip():
        params['cc'] = cc.strip()
    if bcc.strip():
        params['bcc'] = bcc.strip()

    query_str = urllib.parse.urlencode(params, quote_via=urllib.parse.quote)
    if query_str:
        return f"mailto:{to.strip()}?{query_str}"
    return f"mailto:{to.strip()}"


def build_phone_payload(phone_number: str, default_region: str = "IN") -> str:
    """Builds standard tel: URI with clean dialable international digits."""
    clean = clean_phone_val(phone_number, default_region)
    digits = clean.replace(" ", "").replace("-", "").replace("(", "").replace(")", "")
    return f"tel:{digits}"


def build_sms_payload(phone_number: str, message: str = "", default_region: str = "IN") -> str:
    """Builds standard SMSTO payload for universal iOS/Android support."""
    clean = clean_phone_val(phone_number, default_region)
    digits = clean.replace(" ", "").replace("-", "").replace("(", "").replace(")", "")
    if message.strip():
        return f"SMSTO:{digits}:{message.strip()}"
    return f"SMSTO:{digits}:"


def build_whatsapp_payload(phone_number: str, message: str = "", default_region: str = "IN") -> str:
    """
    Builds direct WhatsApp chat link with clean country code and digits.
    Works directly in browser, iOS WhatsApp, and Android WhatsApp.
    """
    clean = clean_phone_val(phone_number, default_region)
    digits = clean.replace("+", "").replace(" ", "").replace("-", "").replace("(", "").replace(")", "")
    if message.strip():
        encoded = urllib.parse.quote(message.strip())
        return f"https://wa.me/{digits}?text={encoded}"
    return f"https://wa.me/{digits}"


def build_location_payload(latitude: float, longitude: float, label: str = "") -> str:
    """
    Builds Google Maps query URL.
    Scanned on iOS -> opens Apple Maps or Google Maps prompt.
    Scanned on Android -> opens Google Maps app directly.
    """
    if label.strip():
        encoded_label = urllib.parse.quote(label.strip())
        return f"https://maps.google.com/?q={latitude},{longitude}+({encoded_label})"
    return f"https://maps.google.com/?q={latitude},{longitude}"


def build_calendar_payload(
    title: str,
    start_dt: datetime,
    end_dt: datetime,
    location: str = "",
    description: str = "",
    all_day: bool = False
) -> str:
    """
    Builds standard iCalendar (.ics / vEvent) payload.
    Prompts 1-tap 'Add to Calendar' on both iOS and Android.
    """
    def esc_ical(text: str) -> str:
        return text.replace('\\', '\\\\').replace(';', '\\;').replace(',', '\\,').replace('\n', '\\n')

    if all_day:
        dtstart = start_dt.strftime("%Y%m%d")
        dtend = end_dt.strftime("%Y%m%d")
        dt_lines = [
            f"DTSTART;VALUE=DATE:{dtstart}",
            f"DTEND;VALUE=DATE:{dtend}"
        ]
    else:
        dtstart = start_dt.strftime("%Y%m%dT%H%M%SZ")
        dtend = end_dt.strftime("%Y%m%dT%H%M%SZ")
        dt_lines = [
            f"DTSTART:{dtstart}",
            f"DTEND:{dtend}"
        ]

    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//QR Master//Universal Event//EN",
        "BEGIN:VEVENT",
        f"SUMMARY:{esc_ical(title.strip())}",
    ] + dt_lines

    if location.strip():
        lines.append(f"LOCATION:{esc_ical(location.strip())}")
    if description.strip():
        lines.append(f"DESCRIPTION:{esc_ical(description.strip())}")

    lines.extend([
        "END:VEVENT",
        "END:VCALENDAR"
    ])
    return "\r\n".join(lines)


def build_upi_payload(
    vpa: str,
    payee_name: str = "",
    amount: float = 0.0,
    note: str = "",
    currency: str = "INR"
) -> str:
    """Builds standard UPI payment URI (Google Pay, PhonePe, Paytm, etc.)."""
    params = [("pa", vpa.strip())]
    if payee_name.strip():
        params.append(("pn", payee_name.strip()))
    if amount > 0:
        params.append(("am", f"{amount:.2f}"))
    params.append(("cu", currency.strip() or "INR"))
    if note.strip():
        params.append(("tn", note.strip()))

    query = urllib.parse.urlencode(params, quote_via=urllib.parse.quote)
    return f"upi://pay?{query}"


def build_social_payload(platform: str, identifier: str) -> str:
    """Builds direct social media links."""
    clean_id = identifier.strip().lstrip("@")
    urls = {
        "instagram": f"https://instagram.com/{clean_id}",
        "linkedin": f"https://linkedin.com/in/{clean_id}" if not clean_id.startswith("http") else clean_id,
        "x": f"https://x.com/{clean_id}",
        "github": f"https://github.com/{clean_id}",
        "youtube": f"https://youtube.com/@{clean_id}" if not clean_id.startswith("http") else clean_id,
        "tiktok": f"https://tiktok.com/@{clean_id}",
        "telegram": f"https://t.me/{clean_id}",
    }
    return urls.get(platform.lower(), identifier.strip())
