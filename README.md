# Universal QR Studio ⚡

A high-performance QR code generator application specifically engineered for **direct 1-tap contact saving across both Apple iOS and Android devices**, along with support for all standard QR payload types, custom styling, logos, and multi-format exports.

---

## 🌟 Flagship Feature: Universal Direct Contact Save

Saving contacts from a scanned QR code can sometimes fail or behave erratically across different devices. Universal QR Studio solves this by strictly implementing **RFC 2426 vCard 3.0** with essential requirements:

| Requirement | Apple iOS (iPhone Camera) | Android (Google Lens / Camera) |
| :--- | :--- | :--- |
| **Trigger Mechanism** | Native yellow banner: *"Add [Name] to Contacts"* | Native action chip: *"Add contact • [Name]"* |
| **Mandatory `FN` (Formatted Name)** | ✅ Required to show contact card banner | ✅ Used as primary contact title |
| **Structured `N` field** | ✅ Populates First, Last, Prefix, Suffix | ✅ Populates device contact fields |
| **Phone Types** | ✅ Correctly maps `CELL`, `WORK`, `HOME` | ✅ Correctly maps Mobile, Work, Home |
| **Structured `ADR`** | ✅ Opens directly into Apple Maps | ✅ Opens directly into Google Maps |
| **Direct Save Action** | 1-Tap creates or merges into Contacts | 1-Tap saves to Google / Device Contacts |

---

## 🚀 Supported QR Code Types

1. **👤 Contact Card (vCard 3.0 / MeCard / vCard 4.0)**:
   - Full Name, Title, Company, Department
   - Mobile, Work, and Home phone numbers
   - Work and Personal email addresses
   - Website, LinkedIn, and social profiles
   - Street address, City, State, ZIP, Country
   - Birthday and Notes/Bio
2. **📶 Wi-Fi Auto-Connect**:
   - WPA/WPA2/WPA3, WEP, Open (nopass)
   - Hidden SSID support
   - Direct 1-tap "Join network" prompt
3. **🌐 Website / URL**: Direct link to any website or portfolio.
4. **💬 WhatsApp Direct Chat**: Opens chat with phone number & pre-filled message without saving contact first.
5. **✉️ Email Message**: Pre-populates recipient, subject, body, CC, and BCC.
6. **📱 Phone Call**: One-tap phone dialer prompt (`tel:`).
7. **💬 SMS Message**: Direct SMS compose with draft text (`SMSTO:`).
8. **📍 Location / GPS**: Coordinates that open seamlessly in Apple Maps or Google Maps.
9. **📅 Calendar Event**: Standard iCal / vEvent that prompts 1-tap "Add to Calendar".
10. **💳 UPI / Payment**: UPI ID, Payee name, and amount for instant payment apps.
11. **📝 Plain Text / Notes**: Raw notes, secret keys, or custom data.
12. **🔗 Social Media Profiles**: Quick links for LinkedIn, Instagram, X (Twitter), GitHub, YouTube, etc.

---

## 🎨 Visual Styling & Customization

- **Module Shapes**:
  - Rounded Dots
  - Smooth Circles
  - Crisp Classic Squares
  - Gapped Modules
  - Horizontal & Vertical Bars
- **Color Gradients & Themes**:
  - Solid Color
  - Radial Gradient (glow from center)
  - Horizontal Gradient
  - Square Gradient
  - Transparent Background (PNG for dark/light business card designs)
- **Embedded Center Badges / Logos**:
  - Built-in vector icons: Contact, Wi-Fi, WhatsApp, Link, Phone, Email, Location
  - Custom logo upload (PNG, JPG, WebP) with auto-centering and anti-aliasing
  - Automatic upgrade to **Error Correction Level H (30%)** to guarantee 100% scan reliability

---

## 📥 Export Formats

- **💾 PNG (300 DPI)**: High-resolution raster image ready for web, screens, and standard print.
- **📐 Vector SVG**: Scalable vector graphics for infinite resolution on flyers, posters, and laser engraving.
- **📇 .VCF Contact File**: Direct electronic business card for importing into Outlook, Apple Contacts, or Google Contacts.
- **📄 Printable Badge (PDF)**: Clean A6 printable digital contact card badge with QR code and contact details.

---

## 🛠️ Architecture

- [`app.py`](file:///c:/Users/Jaspreet/Documents/QR%20Gen/app.py): Main interactive Streamlit application with custom glassmorphic styling and two-column responsive layout.
- [`qr_payloads.py`](file:///c:/Users/Jaspreet/Documents/QR%20Gen/qr_payloads.py): Standards-compliant payload generator for vCard 3.0/4.0, MeCard, Wi-Fi, WhatsApp, iCal, UPI, and URLs.
- [`qr_renderer.py`](file:///c:/Users/Jaspreet/Documents/QR%20Gen/qr_renderer.py): High-resolution PIL/StyledPil renderer, gradient engine, center badge embedder, SVG exporter, and FPDF card generator.
- [`presets.py`](file:///c:/Users/Jaspreet/Documents/QR%20Gen/presets.py): Pre-configured profiles (Executive, Creative Director, Medical Specialist, Coffee Shop Wi-Fi, etc.) for instant testing.
- `assets/`: Crisp vector/anti-aliased icon badges for center logo embedding.
