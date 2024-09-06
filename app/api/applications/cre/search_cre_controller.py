import re
from sqlmodel import select, func
from fastapi import HTTPException, status
from sqlmodel import Session

from models.search_for_cre_history import SearchForCreHistory
from models.users import User
from models.factors import (
    Factors,
    FactorsListOut,
    FactorsOut,
    MotifSearch,
    MotifSearchAndSaveHistoryOut,
    MotifSearchOut,
    QueryCreSearchIn,
    Position,
)
from models.factors_function_labels import FactorsFunctionLabels
from core.config import settings


def search_for_cre(session: Session, data_in: MotifSearch) -> MotifSearchOut:
    reverse_complement = rev_comp_st(data_in.sequence)
    db_factors = session.exec(select(Factors).order_by(Factors.ft_id)).all()
    database = {factor.ac: factor.sq for factor in db_factors}

    # Find matches on both strands
    forward_matches = find_sequence_in_database(data_in.sequence, database)
    reverse_matches = find_sequence_in_database(reverse_complement, database)

    # Group matches by factor_id
    forward_matches_grouped = {}
    for match in forward_matches:
        factor_id = match[1]
        if factor_id not in forward_matches_grouped:
            forward_matches_grouped[factor_id] = []
        forward_matches_grouped[factor_id].append(
            Position(start=match[2], end=match[3])
        )  # Store start, end

    reverse_matches_grouped = {}
    for match in reverse_matches:
        factor_id = match[1]
        if factor_id not in reverse_matches_grouped:
            reverse_matches_grouped[factor_id] = []
        reverse_matches_grouped[factor_id].append(
            Position(start=match[2], end=match[3])
        )  # Store start, end

    # Prepare data for matches with color, only one entry per factor_id
    forward_matches_with_color = []
    for factor_id, positions in forward_matches_grouped.items():
        factor = session.exec(select(Factors).where(Factors.ac == factor_id)).first()
        if not factor:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Factor with AC {factor_id} not found.",
            )

        function_label = None
        if factor.ft_id:
            function_label = session.exec(
                select(FactorsFunctionLabels).where(
                    FactorsFunctionLabels.id == factor.ft_id
                )
            ).first()

        forward_matches_with_color.append(
            {
                "factor_id": factor_id,
                "sq": factor.sq,
                "de": factor.de,
                "function_label": function_label,
                "positions": positions,  # Store start, end as an array
                "color": factor.color,
            }
        )

    reverse_matches_with_color = []
    for factor_id, positions in reverse_matches_grouped.items():
        factor = session.exec(select(Factors).where(Factors.ac == factor_id)).first()
        if not factor:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Factor with AC {factor_id} not found.",
            )
        function_label = None
        if factor.ft_id:
            function_label = session.exec(
                select(FactorsFunctionLabels).where(
                    FactorsFunctionLabels.id == factor.ft_id
                )
            ).first()

        reverse_matches_with_color.append(
            {
                "factor_id": factor_id,
                "sq": factor.sq,
                "de": factor.de,
                "function_label": function_label,
                "positions": positions,  # Store start, end as an array
                "color": factor.color,
            }
        )

    data = {
        "original_sequence": data_in.sequence,
        "reverse_complement_sequence": reverse_complement,
        "forward_strand_matches": forward_matches_with_color,
        "reverse_strand_matches": reverse_matches_with_color,
    }
    return data


def search_for_cre_and_save_history(
    session: Session, data_in: MotifSearch, user_id: int
) -> MotifSearchAndSaveHistoryOut:
    db_user = session.exec(select(User).where(User.id == user_id)).first()
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found.",
        )

    # Save search history
    db_search_history = SearchForCreHistory(
        sequences=data_in.sequence,
        user_id=user_id,
    )
    session.add(db_search_history)
    session.commit()
    session.refresh(db_search_history)

    reverse_complement = rev_comp_st(data_in.sequence)
    db_factors = session.exec(select(Factors).order_by(Factors.ft_id)).all()
    database = {factor.ac: factor.sq for factor in db_factors}

    # Find matches on both strands
    forward_matches = find_sequence_in_database(data_in.sequence, database)
    reverse_matches = find_sequence_in_database(reverse_complement, database)

    # Group matches by factor_id
    forward_matches_grouped = {}
    for match in forward_matches:
        factor_id = match[1]
        if factor_id not in forward_matches_grouped:
            forward_matches_grouped[factor_id] = []
        forward_matches_grouped[factor_id].append(
            Position(start=match[2], end=match[3])
        )  # Store start, end

    reverse_matches_grouped = {}
    for match in reverse_matches:
        factor_id = match[1]
        if factor_id not in reverse_matches_grouped:
            reverse_matches_grouped[factor_id] = []
        reverse_matches_grouped[factor_id].append(
            Position(start=match[2], end=match[3])
        )  # Store start, end

    # Prepare data for matches with color, only one entry per factor_id
    forward_matches_with_color = []
    for factor_id, positions in forward_matches_grouped.items():
        factor = session.exec(select(Factors).where(Factors.ac == factor_id)).first()
        if not factor:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Factor with AC {factor_id} not found.",
            )

        function_label = None
        if factor.ft_id:
            function_label = session.exec(
                select(FactorsFunctionLabels).where(
                    FactorsFunctionLabels.id == factor.ft_id
                )
            ).first()

        forward_matches_with_color.append(
            {
                "factor_id": factor_id,
                "sq": factor.sq,
                "de": factor.de,
                "function_label": function_label,
                "positions": positions,  # Store start, end as an array
                "color": factor.color,
            }
        )

    reverse_matches_with_color = []
    for factor_id, positions in reverse_matches_grouped.items():
        factor = session.exec(select(Factors).where(Factors.ac == factor_id)).first()
        if not factor:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Factor with AC {factor_id} not found.",
            )
        function_label = None
        if factor.ft_id:
            function_label = session.exec(
                select(FactorsFunctionLabels).where(
                    FactorsFunctionLabels.id == factor.ft_id
                )
            ).first()

        reverse_matches_with_color.append(
            {
                "factor_id": factor_id,
                "sq": factor.sq,
                "de": factor.de,
                "function_label": function_label,
                "positions": positions,  # Store start, end as an array
                "color": factor.color,
            }
        )

    data = {
        "original_sequence": data_in.sequence,
        "reverse_complement_sequence": reverse_complement,
        "forward_strand_matches": forward_matches_with_color,
        "reverse_strand_matches": reverse_matches_with_color,
        "history_id": db_search_history.id,
    }
    return data


def rev_comp_st(seq):
    """Tạo chuỗi DNA đảo ngược bổ sung."""
    complement = {"A": "T", "T": "A", "C": "G", "G": "C"}
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


def query_cre(
    session: Session,
    data_in: QueryCreSearchIn,
    skip: int = 0,
    limit: int = settings.RECORD_LIMIT,
) -> FactorsListOut:
    factors = select(Factors)

    if data_in.id:
        factors = factors.where(Factors.id == data_in.id)
    if data_in.ac:
        factors = factors.where(Factors.ac.ilike(f"%{data_in.ac}%"))
    if data_in.dt:
        factors = factors.where(Factors.dt.ilike(f"%{data_in.dt}%"))
    if data_in.de:
        factors = factors.where(Factors.de.ilike(f"%{data_in.de}%"))
    if data_in.kw:
        factors = factors.where(Factors.kw.ilike(f"%{data_in.kw}%"))
    if data_in.os:
        factors = factors.where(Factors.os.ilike(f"%{data_in.os}%"))
    if data_in.ra:
        factors = factors.where(Factors.ra.ilike(f"%{data_in.ra}%"))
    if data_in.rt:
        factors = factors.where(Factors.rt.ilike(f"%{data_in.rt}%"))
    if data_in.rl:
        factors = factors.where(Factors.rl.ilike(f"%{data_in.rl}%"))
    if data_in.rd:
        factors = factors.where(Factors.rd.ilike(f"%{data_in.rd}%"))
    if data_in.sq:
        factors = factors.where(Factors.sq.ilike(f"%{data_in.sq}%"))

    count_subquery = factors.subquery()
    count_statement = select(func.count()).select_from(count_subquery)
    count = session.exec(count_statement).one()

    factors = factors.offset(skip).limit(limit)
    db_factors = session.exec(factors).all()

    response_data = []

    ft_ids = [factor.ft_id for factor in db_factors]

    function_labels = session.exec(
        select(FactorsFunctionLabels).where(FactorsFunctionLabels.id.in_(ft_ids))
    ).all()

    function_labels_dict = {fl.id: fl for fl in function_labels}

    # get function labels
    for item in db_factors:
        function_label = None
        if item.ft_id:
            function_label = function_labels_dict.get(item.ft_id)
        response_data.append(
            FactorsOut(**item.model_dump(), function_label=function_label)
        )

    return FactorsListOut(data=response_data, count=count)
