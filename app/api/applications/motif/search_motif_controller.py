import re
from sqlmodel import select
from fastapi import HTTPException, status
from sqlmodel import Session

from models.factors import Factors, MotifSearch, MotifSearchOut


def search_motif(session: Session, data_in: MotifSearch) -> MotifSearchOut:
    reverse_complement = rev_comp_st(data_in.sequence)
    db_factors = session.exec(select(Factors)).all()
    database = {factor.ac: factor.sq for factor in db_factors}

    # Find matches on both strands
    forward_matches = find_sequence_in_database(data_in.sequence, database)
    reverse_matches = find_sequence_in_database(reverse_complement, database)

    # Prepare data for matches with color
    forward_matches_with_color = []
    for match in forward_matches:
        factor_id = match[1]
        factor = session.exec(select(Factors).where(Factors.ac == factor_id)).first()
        if not factor:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Factor with AC {factor_id} not found.")
        
        forward_matches_with_color.append({
            "factor_id": factor_id,
            "start": match[2],
            "end": match[3],
            "color": factor.color
        })

    reverse_matches_with_color = []
    for match in reverse_matches:
        factor_id = match[1]
        factor = session.exec(select(Factors).where(Factors.ac == factor_id)).first()
        if not factor:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Factor with AC {factor_id} not found.")
        
        reverse_matches_with_color.append({
            "factor_id": factor_id,
            "start": match[2],
            "end": match[3],
            "color": factor.color
        })

    # Serialize factors
    found_factor_ids = {match[1] for match in forward_matches + reverse_matches}
    found_factors = session.exec(select(Factors).where(Factors.ac.in_(found_factor_ids))).all()

    data = {
        "original_sequence": data_in.sequence,
        "reverse_complement_sequence": reverse_complement,
        "forward_strand_matches": forward_matches_with_color,
        "reverse_strand_matches": reverse_matches_with_color,
        "factors": found_factors
    }
    return data

def rev_comp_st(seq):
    """Tạo chuỗi DNA đảo ngược bổ sung."""
    complement = {'A': 'T', 'T': 'A', 'C': 'G', 'G': 'C'}
    return "".join(complement.get(base, base) for base in reversed(seq)).upper()

def iupac_to_regex(substring):
    """Chuyển đổi chuỗi IUPAC thành biểu thức chính quy."""
    iupac_codes = {
        "R": "[AG]",
        "Y": "[CT]",
        "S": "[GC]",
        "W": "[AT]",
        "K": "[GT]",
        "M": "[AC]",
        "B": "[CGT]",
        "D": "[AGT]",
        "H": "[ACT]",
        "V": "[ACG]",
        "N": "[ACGT]",
    }
    pattern = ""
    for char in substring:
        if char in iupac_codes:
            pattern += iupac_codes[char]
        else:
            pattern += char
    return pattern

def find_sequence_in_database(fragment_dna, database):
    """Tìm kiếm chuỗi DNA khớp trong database."""
    found_sequences = []
    for key, value in database.items():
        for match in re.finditer(iupac_to_regex(value), fragment_dna):
            start = match.start()
            end = start + len(value)
            found_sequences.append((value, key, start, end))
    return found_sequences