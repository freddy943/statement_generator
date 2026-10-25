import streamlit as st
import pandas as pd
from fpdf import FPDF
import pdfplumber
import os
import re

# --- FPDF KLASA ZA "ZEBRA" DIZAJN ---
class ModernSettlementPDF(FPDF):
    def __init__(self):
        super().__init__()
        self.c_accent = (238, 75, 43)      
        self.c_dark = (40, 40, 40)         
        self.c_gray = (130, 130, 130)      
        self.c_light = (248, 248, 250)     

    def header(self):
        # Dekorativna akcentna traka
        self.set_fill_color(*self.c_accent)
        self.rect(0, 0, 210, 4, 'F')

        # Logo na lijevoj strani (BEZ adrese ispod)
        if os.path.exists("3JmMvy1.png"):
            self.image("3JmMvy1.png", 15, 12, 70) 
        else:
            self.set_font('Arial', 'B', 18)
            self.set_text_color(*self.c_accent)
            self.set_y(15)
            self.set_x(15)
            self.cell(0, 8, 'BOBBINDOTS TRANSPORT LLC', ln=True, align='L')
        
        # Novi naslov i adresa na desnoj strani
        self.set_y(15)
        self.set_font('Arial', 'B', 24)
        self.set_text_color(*self.c_accent)
        self.cell(0, 10, 'DRIVER SETTLEMENT', ln=True, align='R')
        
        self.set_font('Arial', '', 10)
        self.set_text_color(*self.c_gray)
        self.cell(0, 5, '159 Crocker Park Blvd, 4th Floor.', ln=True, align='R')
        self.cell(0, 5, 'Westlake, OH 44145', ln=True, align='R')
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.set_text_color(*self.c_gray)
        self.cell(0, 10, 'Bobbindots Transport LLC - Internal Settlement Report', 0, 0, 'L')
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'R')

    def add_driver_info(self, s_no, s_date, period, status, driver, d_id, truck, trailer):
        self.ln(5)
        self.set_draw_color(230, 230, 230)
        self.set_line_width(0.2)
        
        # Red 1 - Kartice
        self.set_x(15)
        self.set_font('Arial', 'B', 7)
        self.set_text_color(*self.c_gray)
        self.set_fill_color(*self.c_light)
        self.cell(45, 5, 'STATEMENT NO.', 'LTR', 0, 'L', True)
        self.cell(45, 5, 'STATEMENT DATE', 'LTR', 0, 'L', True)
        self.cell(45, 5, 'PAY PERIOD', 'LTR', 0, 'L', True)
        self.cell(45, 5, 'STATUS', 'LTR', 1, 'L', True)

        self.set_x(15)
        self.set_font('Arial', 'B', 10)
        self.set_text_color(*self.c_dark)
        self.cell(45, 7, s_no, 'LBR', 0, 'L', True)
        self.cell(45, 7, s_date, 'LBR', 0, 'L', True)
        self.cell(45, 7, period, 'LBR', 0, 'L', True)
        self.cell(45, 7, status, 'LBR', 1, 'L', True)
        self.ln(2)

        # Red 2 - Kartice
        self.set_x(15)
        self.set_font('Arial', 'B', 7)
        self.set_text_color(*self.c_gray)
        self.cell(60, 5, 'DRIVER NAME (ID)', 'LTR', 0, 'L', True)
        self.cell(60, 5, 'TRUCK NO.', 'LTR', 0, 'L', True)
        self.cell(60, 5, 'TRAILER NO.', 'LTR', 1, 'L', True)

        self.set_x(15)
        self.set_font('Arial', 'B', 10)
        self.set_text_color(*self.c_dark)
        d_text = f"{driver} ({d_id})" if d_id else driver
        self.cell(60, 7, d_text, 'LBR', 0, 'L', True)
        self.cell(60, 7, truck, 'LBR', 0, 'L', True)
        self.cell(60, 7, trailer, 'LBR', 1, 'L', True)
        self.ln(8)

    def draw_modern_table_header(self, title, cols, widths, font_size=8):
        self.ln(4)
        self.set_x(15)
        self.set_font('Arial', 'B', 11)
        self.set_text_color(*self.c_accent)
        self.cell(0, 8, title.upper(), 0, 1, 'L')
        
        self.set_x(15)
        self.set_fill_color(45, 45, 45) 
        self.set_text_color(255, 255, 255)
        self.set_font('Arial', 'B', font_size)
        for col, width in zip(cols, widths):
            self.cell(width, 9, col, 0, 0, 'C', True)
        self.ln()

    def draw_modern_table_row(self, row_data, widths, is_even, is_deduction=False, font_size=9):
        self.set_x(15)
        self.set_font('Arial', '', font_size)
        
        if is_even:
            self.set_fill_color(245, 245, 245)
        else:
            self.set_fill_color(255, 255, 255)
            
        for i, (data, width) in enumerate(zip(row_data, widths)):
            self.set_text_color(60, 60, 60)
            if i == len(row_data) - 1: 
                self.set_font('Arial', 'B', font_size)
                if is_deduction:
                    self.set_text_color(200, 50, 50)
            
            text_val = str(data)
            if len(text_val) > 35 and font_size <= 8:
                text_val = text_val[:32] + "..."
                
            self.cell(width, 8, text_val, 0, 0, 'C', True)
            self.set_font('Arial', '', font_size) 
        self.ln()

    def draw_summary(self, t_trips, t_deds, t_fuel, net):
        self.ln(8)
        self.set_x(115)
        self.set_font('Arial', '', 10)
        self.set_text_color(*self.c_gray)
        self.cell(40, 7, 'Total Trip Pay:', 0, 0, 'R')
        self.set_font('Arial', 'B', 10)
        self.set_text_color(*self.c_dark)
        self.cell(40, 7, f'${t_trips:,.2f}', 0, 1, 'R')
        
        self.set_x(115)
        self.set_font('Arial', '', 10)
        self.set_text_color(*self.c_gray)
        self.cell(40, 7, 'Total Deductions:', 0, 0, 'R')
        self.set_font('Arial', 'B', 10)
        self.set_text_color(210, 40, 40) 
        self.cell(40, 7, f'-${t_deds:,.2f}', 0, 1, 'R')

        self.set_x(115)
        self.set_font('Arial', '', 10)
        self.set_text_color(*self.c_gray)
        self.cell(40, 7, 'Fuel Card Deductions:', 0, 0, 'R')
        self.set_font('Arial', 'B', 10)
        self.set_text_color(210, 40, 40) 
        self.cell(40, 7, f'-${t_fuel:,.2f}', 0, 1, 'R')
        
        self.ln(3)
        self.set_x(115)
        self.set_fill_color(*self.c_accent)
        self.set_text_color(255, 255, 255)
        self.set_font('Arial', 'B', 13)
        self.cell(45, 12, ' NET SETTLEMENT', 0, 0, 'L', True)
        self.cell(35, 12, f'${net:,.2f} ', 0, 1, 'R', True)


# --- FUNKCIJA ZA EKSTRAKCIJU IZ PDF-a ---
def parse_protransport_pdf(file_obj):
    extracted_data = {
        "driver": "", "date": "", "unit": "",
        "trips": [], "deductions": [], "fuel": []
    }
    
    with pdfplumber.open(file_obj) as pdf:
        text = ""
        for page in pdf.pages:
            text += page.extract_text() + "\n"
            
    lines = text.split('\n')
    current_section = None
    
    for i, line in enumerate(lines):
        line = line.strip()
        if not line: continue
        
        if "Unit #" in line:
            parts = line.split("Unit #")
            if len(parts) > 1:
                extracted_data["unit"] = parts[1].strip()
        elif re.match(r'^\d{1,2}/\d{1,2}/\d{4}$', line):
            extracted_data["date"] = line
        elif i > 3 and i < 10 and not extracted_data["driver"] and "Statement" not in line and "Unit" not in line and not re.search(r'\d', line):
             extracted_data["driver"] = line
             
        if "Trips" in line and "Trip No." not in line:
            current_section = "trips"
            continue
        elif "Advances and Deductions:" in line or "Advances and Deductions" in line:
            current_section = "deductions"
            continue
        elif "Fuel Card:" in line or "Fuel Card" in line:
            current_section = "fuel"
            continue
        elif "Total:" in line or "Check Amount:" in line:
            pass 
            
        if current_section == "trips":
            match = re.match(r'^(\d+)\s+(.+?)\s+(\d+)\s+\$?([\d\.,]+)\s+(\d{1,2}/\d{1,2}/\d{4})\s+\$?([\d\.,]+)$', line)
            if match:
                extracted_data["trips"].append({
                    "Trip No.": match.group(1),
                    "Description": match.group(2),
                    "Mileage": match.group(3),
                    "Freight Amount": float(match.group(4).replace(',', '')),
                    "Date": match.group(5),
                    "Amount": float(match.group(6).replace(',', ''))
                })
                
        elif current_section == "deductions":
            match = re.search(r'^(.*?)\s+(\d{1,2}/\d{1,2}/\d{4})\s+[\(\-]?\$?([\d\.,]+)\)?$', line)
            if match and "Description" not in line:
                extracted_data["deductions"].append({
                    "Description": match.group(1).strip(),
                    "Date": match.group(2),
                    "Amount": float(match.group(3).replace(',', ''))
                })
                
        elif current_section == "fuel":
            match = re.search(r'^(.*?)\s+([\d\.,]+)\s+[\(\-]?\$?([\d\.,]+)\)?\s+[\(\-]?\$?([\d\.,]+)\)?\s+[\(\-]?\$?([\d\.,]+)\)?\s+(\d{1,2}/\d{1,2}/\d{4})\s+[\(\-]?\$?([\d\.,]+)\)?$', line)
            if match and "Description" not in line:
                prefix = match.group(1).strip()
                state = ""
                city = ""
                desc = prefix
                
                prefix_parts = prefix.split()
                if len(prefix_parts) >= 2 and len(prefix_parts[-1]) == 2 and prefix_parts[-1].isupper():
                    state = prefix_parts[-1]
                    city = prefix_parts[-2]
                    desc = " ".join(prefix_parts[:-2])
                
                extracted_data["fuel"].append({
                    "Description": desc,
                    "City": city.replace(',', ''),
                    "St.": state,
                    "Gallons": match.group(2),
                    "Fuel ($)": match.group(3),
                    "Advance ($)": match.group(4),
                    "Misc. ($)": match.group(5),
                    "Date": match.group(6),
                    "Amount": float(match.group(7).replace(',', ''))
                })

    return extracted_data


# --- STREAMLIT APLIKACIJA ---
st.set_page_config(page_title="Driver Settlement Automator", layout="wide")

if os.path.exists("3JmMvy1.png"):
    st.image("3JmMvy1.png", width=250)
else:
    st.title("🚛 Bobbindots - Driver Settlement Automator")

if 'data_loaded' not in st.session_state:
    st.session_state.data_loaded = False
    st.session_state.driver_info = {"name": "", "date": "", "unit": ""}
    st.session_state.trips_df = pd.DataFrame(columns=["Trip No.", "Description", "Mileage", "Freight Amount", "Date", "Amount"])
    st.session_state.deds_df = pd.DataFrame(columns=["Description", "Date", "Amount"])
    st.session_state.fuel_df = pd.DataFrame(columns=["Description", "City", "St.", "Gallons", "Fuel ($)", "Advance ($)", "Misc. ($)", "Date", "Amount"])

st.subheader("1. Otpremanje starog dokumenta")
uploaded_pdf = st.file_uploader("Otpremi PDF statement iz ProTransporta", type=['pdf'])

if st.session_state.data_loaded:
    if st.button("🔄 Očisti i učitaj novi fajl"):
        st.session_state.data_loaded = False
        st.rerun()

if uploaded_pdf is not None and not st.session_state.data_loaded:
    with st.spinner("Parsiranje PDF-a..."):
        parsed_data = parse_protransport_pdf(uploaded_pdf)
        
        st.session_state.driver_info["name"] = parsed_data["driver"]
        st.session_state.driver_info["date"] = parsed_data["date"]
        st.session_state.driver_info["unit"] = parsed_data["unit"]
        
        if parsed_data["trips"]:
            st.session_state.trips_df = pd.DataFrame(parsed_data["trips"])
        if parsed_data["deductions"]:
            st.session_state.deds_df = pd.DataFrame(parsed_data["deductions"])
        if parsed_data["fuel"]:
            st.session_state.fuel_df = pd.DataFrame(parsed_data["fuel"])
            
        st.session_state.data_loaded = True
        st.rerun()

st.divider()

st.subheader("2. Provjera i uređivanje podataka")
col1, col2, col3, col4 = st.columns(4)

with col1:
    s_no = st.text_input("Statement No:", value="#STL-2026-9042")
    driver = st.text_input("Driver Name:", value=st.session_state.driver_info["name"])
with col2:
    s_date = st.text_input("Statement Date:", value=st.session_state.driver_info["date"])
    d_id = st.text_input("Driver ID:", value="")
with col3:
    period = st.text_input("Pay Period:", value="09/14/2026 - 09/20/2026")
    truck = st.text_input("Truck No:", value=st.session_state.driver_info["unit"])
with col4:
    status = st.text_input("Status:", value="Independent Contractor")
    trailer = st.text_input("Trailer No:", value="")

st.write("**Trips**")
edited_trips = st.data_editor(st.session_state.trips_df, num_rows="dynamic", use_container_width=True)

st.write("**Advances and Deductions**")
edited_deds = st.data_editor(st.session_state.deds_df, num_rows="dynamic", use_container_width=True)

st.write("**Fuel Card**")
edited_fuel = st.data_editor(st.session_state.fuel_df, num_rows="dynamic", use_container_width=True)


total_trips = sum(pd.to_numeric(edited_trips["Amount"], errors='coerce').fillna(0)) if not edited_trips.empty else 0
total_deds = sum(pd.to_numeric(edited_deds["Amount"], errors='coerce').fillna(0)) if not edited_deds.empty else 0
total_fuel = sum(pd.to_numeric(edited_fuel["Amount"], errors='coerce').fillna(0)) if not edited_fuel.empty else 0
net_settlement = total_trips - total_deds - total_fuel


if st.button("Generiši Moderni Statement PDF", type="primary"):
    pdf = ModernSettlementPDF()
    pdf.add_page()
    
    pdf.add_driver_info(s_no, s_date, period, status, driver, d_id, truck, trailer)

    if not edited_trips.empty:
        df_trips = edited_trips.dropna(how='all').copy()
        df_trips["Freight Amount"] = df_trips["Freight Amount"].apply(lambda x: f"${float(x):.2f}")
        df_trips["Amount"] = df_trips["Amount"].apply(lambda x: f"${float(x):.2f}")
        
        cols = ["Trip No.", "Description", "Mileage", "Freight Amt", "Date", "Amount"]
        widths = [20, 70, 15, 25, 25, 25] 
        pdf.draw_modern_table_header("Trips", cols, widths, font_size=8)
        
        for index, row in df_trips.reset_index().iterrows():
            pdf.draw_modern_table_row([row["Trip No."], row["Description"], row["Mileage"], row["Freight Amount"], row["Date"], row["Amount"]], widths, index % 2 == 0)

    if not edited_deds.empty:
        df_deds = edited_deds.dropna(how='all').copy()
        df_deds["Amount"] = df_deds["Amount"].apply(lambda x: f"-${float(x):.2f}")
        
        cols = ["Description", "Date", "Amount"]
        widths = [110, 40, 30] 
        pdf.draw_modern_table_header("Advances and Deductions", cols, widths, font_size=9)
        
        for index, row in df_deds.reset_index().iterrows():
            pdf.draw_modern_table_row([row["Description"], row["Date"], row["Amount"]], widths, index % 2 == 0, is_deduction=True)
        
    if not edited_fuel.empty:
        df_fuel = edited_fuel.dropna(how='all').copy()
        df_fuel["Amount"] = df_fuel["Amount"].apply(lambda x: f"-${float(x):.2f}")
        
        cols = ["Desc", "City", "St.", "Gal", "Fuel ($)", "Adv ($)", "Misc ($)", "Date", "Amount"]
        widths = [35, 25, 10, 15, 18, 18, 18, 18, 23] 
        pdf.draw_modern_table_header("Fuel Card", cols, widths, font_size=7)
        
        for index, row in df_fuel.reset_index().iterrows():
            pdf.draw_modern_table_row([row["Description"], row["City"], row["St."], row["Gallons"], row["Fuel ($)"], row["Advance ($)"], row["Misc. ($)"], row["Date"], row["Amount"]], widths, index % 2 == 0, is_deduction=True, font_size=7.5)

    pdf.draw_summary(total_trips, total_deds, total_fuel, net_settlement)

    file_name = f"Settlement_{driver.replace(' ', '_')}.pdf"
    pdf.output(file_name)
    
    with open(file_name, "rb") as pdf_file:
        st.success("Moderni PDF uspješno generisan!")
        st.download_button("⬇️ Preuzmi PDF", data=pdf_file, file_name=file_name, mime='application/pdf')