import streamlit as st
import re

# Seiteneinstellungen
st.set_page_config(
    page_title="E-Commerce AI-Support Cockpit | Demo",
    page_icon="⚡",
    layout="wide"
)

# -------------------------------------------------------------
# 1. MOCK-DATENBANK & LOOKUP TOOL
# -------------------------------------------------------------
MOCK_ORDERS = {
    "1084": {
        "order_number": 1084,
        "customer_name": "Lukas Weber",
        "email": "lukas.weber.test@example.com",
        "order_date": "28. August 2026",
        "status": "Bezahlt",
        "fulfillment_status": "Versandt",
        "items": ["Minimalistischer Leder-Rucksack", "Leder-Pflegebalsam (100ml)"],
        "carrier": "DHL",
        "tracking_number": "00340434289012345678",
        "tracking_url": "https://www.dhl.de/de/privatkunden/pakete-empfangen/verfolgen.html?piececode=00340434289012345678"
    },
    "1085": {
        "order_number": 1085,
        "customer_name": "Sarah Meyer",
        "email": "sarah.m@example.com",
        "order_date": "04. September 2026",
        "status": "Zahlung ausstehend",
        "fulfillment_status": "Nicht versandt",
        "items": ["Sneaker Classic White (Gr. 39)"],
        "carrier": "-",
        "tracking_number": "-",
        "tracking_url": "-"
    }
}

def query_shopify_tool(query_text: str):
    """Sucht nach Bestellnummer oder hinterlegter E-Mail."""
    match = re.search(r"#?(\d{4})", query_text)
    if match:
        order_id = match.group(1)
        if order_id in MOCK_ORDERS:
            return MOCK_ORDERS[order_id]
            
    for order in MOCK_ORDERS.values():
        if order["email"].lower() in query_text.lower():
            return order
            
    return None

# -------------------------------------------------------------
# 2. DEMO-SZENARIEN FÜR INTERESSENTEN
# -------------------------------------------------------------
SCENARIOS = {
    "Paketstatus abfragen (#1084)": "Hallo Support-Team, ich warte seit ein paar Tagen auf meine Bestellung #1084. Wo befindet sich das Paket aktuell? Danke, Lukas Weber",
    "Bestellung stornieren (#1085)": "Moin, ich habe gestern versehentlich Sneaker bestellt (#1085). Die Zahlung ist noch offen. Kann ich die Bestellung noch stornieren? VG Sarah",
    "Unbekannte Bestellung (Fehlende Daten)": "Guten Tag, wo bleibt mein Paket? Ich habe letzte Woche etwas bestellt, weiß aber die Nummer nicht mehr.",
    "Eigene Eingabe": ""
}

# -------------------------------------------------------------
# 3. BENUTZEROBERFLÄCHE: DEMO-COCKPIT
# -------------------------------------------------------------
st.title("⚡ E-Commerce AI Support-Autopilot")
st.caption("Interaktive Live-Demo: Anfragen in Sekunden analysieren, Shop-Daten abrufen und versandfertige Antworten generieren.")

col_left, col_right = st.columns([1, 1], gap="large")

with col_left:
    st.subheader("📥 1. Eingehende Kundenanfrage")
    
    selected_scenario = st.selectbox(
        "Wähle ein typisches Support-Szenario:",
        list(SCENARIOS.keys())
    )
    
    default_text = SCENARIOS[selected_scenario]
    user_input = st.text_area(
        "Kunden-E-Mail:", 
        value=default_text, 
        height=150,
        placeholder="Schreibe eine eigene Kundenanfrage..."
    )
    
    run_button = st.button("🚀 Anfrage durch AI analysieren", type="primary", use_container_width=True)
    
    st.markdown("---")
    st.info("💡 **Für Shop-Betreiber:** Das System greift automatisiert auf dein Warenwirtschafts- oder Shop-System zu, ohne dass manuell gesucht werden muss.")

with col_right:
    st.subheader("🤖 2. Support-Cockpit (Echtzeit-Ergebnis)")
    
    if run_button and user_input.strip():
        with st.spinner("AI prüft Shop-System & generiert Antwort..."):
            order_data = query_shopify_tool(user_input)
            
            # Status-Badges
            col_meta1, col_meta2, col_meta3 = st.columns(3)
            with col_meta1:
                st.metric("Dringlichkeit", "Mittel" if order_data else "Niedrig")
            with col_meta2:
                st.metric("Sentiment", "Fragend / Neutral")
            with col_meta3:
                st.metric("Shop-Match", "Gefunden ✅" if order_data else "Nicht gefunden ❌")
            
            st.markdown("#### 🔍 Ermittelte Daten aus dem Shop:")
            if order_data:
                st.json({
                    "Bestellnummer": f"#{order_data['order_number']}",
                    "Kunde": order_data['customer_name'],
                    "Status": order_data['status'],
                    "Versand": f"{order_data['fulfillment_status']} ({order_data['carrier']})",
                    "Tracking": order_data['tracking_number'],
                    "Artikel": order_data['items']
                })
            else:
                st.warning("Keine übereinstimmende Bestellung im Shop-System gefunden.")

            st.markdown("#### ✉️ Vorgeschlagener E-Mail-Entwurf:")
            
            if order_data and order_data["order_number"] == 1084:
                email_draft = (
                    f"Hallo {order_data['customer_name']},\n\n"
                    f"vielen Dank für deine Nachricht. Deine Bestellung #{order_data['order_number']} "
                    f"wurde bereits erfolgreich verpackt und versandt.\n\n"
                    f"Du kannst den aktuellen Lieferstatus direkt bei {order_data['carrier']} verfolgen:\n"
                    f"🔗 Tracking-Link: {order_data['tracking_url']}\n\n"
                    f"Falls du weitere Fragen hast, antworte einfach direkt auf diese E-Mail.\n\n"
                    f"Herzliche Grüße\nDein Support-Team"
                )
                internal_note = "Paket ist via DHL unterwegs. Tracking-Link wurde automatisch bereitgestellt. Keine manuelle Aktion notwendig."
            elif order_data and order_data["order_number"] == 1085:
                email_draft = (
                    f"Hallo {order_data['customer_name']},\n\n"
                    f"wir haben deine Anfrage zur Stornierung von Bestellung #{order_data['order_number']} erhalten. "
                    f"Da die Ware aktuell noch nicht für den Versand vorbereitet wurde, konnten wir deinen Auftrag problemlos stornieren.\n\n"
                    f"Eine Bestätigung dazu ist bereits an deine E-Mail unterwegs.\n\n"
                    f"Beste Grüße\nDein Support-Team"
                )
                internal_note = "Bestellung war unbezahlt und unversandt. Stornierung im System vorgemerkt."
            else:
                email_draft = (
                    "Hallo,\n\n"
                    "vielen Dank für deine Nachricht. Leider konnten wir anhand deiner Angaben keine aktuelle Bestellung im System finden.\n\n"
                    "Könntest du uns kurz deine Bestellnummer (#xxxx) oder die E-Mail-Adresse nennen, mit der bestellt wurde? Dann prüfen wir den Status sofort für dich nach.\n\n"
                    "Freundliche Grüße\nDein Support-Team"
                )
                internal_note = "Keine Daten gefunden. Rückfrage nach Bestellnummer/E-Mail formuliert."

            st.text_area("Versandbereite E-Mail:", value=email_draft, height=220)
            st.caption(f"📌 **Interne Notiz für das Team:** {internal_note}")
            
    elif not run_button:
        st.info("Wähle links ein Szenario aus und klicke auf 'Anfrage durch AI analysieren', um die Demo zu starten.")

# -------------------------------------------------------------
# 4. ROI-RECHNER & CALL TO ACTION
# -------------------------------------------------------------
st.markdown("---")
st.header("📈 Dein Sparpotenzial: Was kostet dich manueller Support wirklich?")
st.caption("Ermittle in Sekunden, wie viel Zeit und Geld du durch intelligente Support-Automation monatlich zurückholst.")

col_calc1, col_calc2 = st.columns([1, 1], gap="large")

with col_calc1:
    st.subheader("⚙️ Deine aktuellen Kennzahlen")
    monthly_tickets = st.slider(
        "Monatliche Support-Tickets:",
        min_value=100,
        max_value=5000,
        value=600,
        step=50,
        help="Typische Anfragen wie 'Wo ist mein Paket?', Stornierungen, Retouren etc."
    )
    
    hourly_wage = st.slider(
        "Kosten pro Support-Mitarbeiter / Stunde (€):",
        min_value=15,
        max_value=60,
        value=25,
        step=1,
        help="Reallohn inkl. Lohnnebenkosten oder dein eigener kalkulatorischer Stundensatz."
    )

    avg_minutes_per_ticket = 6  # Durchschnittliche Bearbeitungsdauer manuell in Minuten
    automation_rate = 0.70      # Konservativ geschätzt: 70% der Standardfälle automatisiert

with col_calc2:
    st.subheader("💰 Dein monatliches Ergebnis")
    
    # Berechnungen
    total_hours_spent = (monthly_tickets * avg_minutes_per_ticket) / 60
    saved_hours = total_hours_spent * automation_rate
    current_cost = total_hours_spent * hourly_wage
    saved_money = saved_hours * hourly_wage
    
    m_col1, m_col2 = st.columns(2)
    with m_col1:
        st.metric(
            label="Eingesparte Arbeitszeit",
            value=f"{int(saved_hours)} Std. / Mo.",
            delta="Bis zu 70% weniger Routine"
        )
    with m_col2:
        st.metric(
            label="Monatliche Ersparnis",
            value=f"{saved_money:,.0f} €".replace(",", "."),
            delta="Reine Kostenreduktion"
        )
        
    st.success(
        f"💡 **Fazit:** Du gewinnst pro Jahr ca. **{int(saved_hours * 12)} Stunden** Fokuszeit zurück "
        f"und senkst deine Betriebskosten um rund **{saved_money * 12:,.0f} €**.".replace(",", ".")
    )

st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; padding: 20px;'>
        <h2>Bereit, diesen Hebel für deinen Shop umzusetzen?</h2>
        <p style='font-size: 17px; max-width: 650px; margin: 0 auto 20px auto;'>
            Im kostenlosen 30-minütigen Analyse-Gespräch prüfen wir dein Ticket-Aufkommen und zeigen dir genau, wie die Anbindung an dein System reibungslos funktioniert.
        </p>
        <a href='https://calendar.app.google/EbQJY6MZbiYNwSEF9' target='_blank'>
            <button style='background-color: #ff4b4b; color: white; border: none; padding: 15px 30px; font-size: 18px; font-weight: bold; border-radius: 8px; cursor: pointer; box-shadow: 0 4px 14px rgba(255, 75, 75, 0.4);'>
                📅 Jetzt kostenloses Beratungsgespräch sichern
            </button>
        </a>
    </div>
    """,
    unsafe_allow_html=True
)
