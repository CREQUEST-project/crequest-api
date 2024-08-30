import io
from fastapi import HTTPException, status
from sqlmodel import Session, select

from api.applications.cre.search_cre_controller import search_for_cre
from models.factors import Factors, MotifSearch

from openpyxl import Workbook
from openpyxl.styles import Alignment, Font


def export_excel(session: Session, data_in: MotifSearch):
    data_matches = search_for_cre(session, data_in)
    
    workbook = Workbook()
    
    forward_factors_id = [match["factor_id"] for match in data_matches["forward_strand_matches"]]
    reverse_factors_id = [match["factor_id"] for match in data_matches["reverse_strand_matches"]]
    
    forward_factors = session.exec(select(Factors).where(Factors.ac.in_(forward_factors_id))).all()
    reverse_factors = session.exec(select(Factors).where(Factors.ac.in_(reverse_factors_id))).all()
    
    # Forward sheet
    forward_sheet = workbook.active
    forward_sheet.title = "Forward Strand"
    _add_header_row(forward_sheet)
    _add_factor_rows(forward_sheet, forward_factors)
    
    # Reverse sheet
    reverse_sheet = workbook.create_sheet(title="Reverse Strand")
    _add_header_row(reverse_sheet)
    _add_factor_rows(reverse_sheet, reverse_factors)
    
    # Format sheets
    _format_sheet(forward_sheet)
    _format_sheet(reverse_sheet)
    
    output = io.BytesIO()
    workbook.save(output)
    output.seek(0)
    
    return output
    
    
def _add_header_row(sheet):
    sheet.append(["ac", "dt", "de", "kw", "os", "ra", "rt", "rl", "rd", "sq"])
    
    # Style header row
    for row in sheet.iter_rows(min_row=1, max_row=1):
        for cell in row:
            cell.alignment = Alignment(horizontal='center', vertical='center')
            cell.font = Font(size=14, bold=True)

    
def _add_factor_rows(sheet, factors):
    for factor in factors:
        sheet.append([
            factor.ac,
            factor.dt,
            factor.de,
            factor.kw,
            factor.os,
            factor.ra,
            factor.rt,
            factor.rl,
            factor.rd,
            factor.sq,
        ])
    
def _format_sheet(sheet):
    # Align center for all cells
    for row in sheet.iter_rows():
        for cell in row:
            cell.alignment = Alignment(horizontal='center', vertical='center')

    # Auto size columns
    for column in sheet.columns:
        max_length = 0
        column_letter = column[0].column_letter
        for cell in column:
            try:
                if len(str(cell.value)) > max_length:
                    max_length = len(cell.value)
            except:
                pass
        adjusted_width = max_length + 2
        sheet.column_dimensions[column_letter].width = adjusted_width