import asyncio
import os
import re
from sqlmodel import select, func
from fastapi import File, Form, HTTPException, UploadFile, status
from sqlmodel import Session

from models.search_for_care_history import SearchForCareHistory
from models.users import User
from models.factors import (
    Factors,
    FactorsListOut,
    MotifSamplerResponse,
    MotifSearch,
    MotifSearchAndSaveHistoryOut,
    MotifSearchOut,
    QueryCareSearchIn,
)
from core.config import settings


def search_for_care(session: Session, data_in: MotifSearch) -> MotifSearchOut:
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
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Factor with AC {factor_id} not found.",
            )

        forward_matches_with_color.append(
            {
                "factor_id": factor_id,
                "start": match[2],
                "end": match[3],
                "color": factor.color,
            }
        )

    reverse_matches_with_color = []
    for match in reverse_matches:
        factor_id = match[1]
        factor = session.exec(select(Factors).where(Factors.ac == factor_id)).first()
        if not factor:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Factor with AC {factor_id} not found.",
            )

        reverse_matches_with_color.append(
            {
                "factor_id": factor_id,
                "start": match[2],
                "end": match[3],
                "color": factor.color,
            }
        )

    # Serialize factors
    found_factor_ids = {match[1] for match in forward_matches + reverse_matches}
    found_factors = session.exec(
        select(Factors).where(Factors.ac.in_(found_factor_ids))
    ).all()

    data = {
        "original_sequence": data_in.sequence,
        "reverse_complement_sequence": reverse_complement,
        "forward_strand_matches": forward_matches_with_color,
        "reverse_strand_matches": reverse_matches_with_color,
        "factors": found_factors,
    }
    return data


def search_for_care_and_save_history(
    session: Session, data_in: MotifSearch, user_id: int
) -> MotifSearchAndSaveHistoryOut:
    db_user = session.exec(select(User).where(User.id == user_id)).first()
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found.",
        )
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
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Factor with AC {factor_id} not found.",
            )

        forward_matches_with_color.append(
            {
                "factor_id": factor_id,
                "start": match[2],
                "end": match[3],
                "color": factor.color,
            }
        )

    reverse_matches_with_color = []
    for match in reverse_matches:
        factor_id = match[1]
        factor = session.exec(select(Factors).where(Factors.ac == factor_id)).first()
        if not factor:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Factor with AC {factor_id} not found.",
            )

        reverse_matches_with_color.append(
            {
                "factor_id": factor_id,
                "start": match[2],
                "end": match[3],
                "color": factor.color,
            }
        )

    # Serialize factors
    found_factor_ids = {match[1] for match in forward_matches + reverse_matches}
    found_factors = session.exec(
        select(Factors).where(Factors.ac.in_(found_factor_ids))
    ).all()

    # Save search history
    db_search_history = SearchForCareHistory(
        sequences=data_in.sequence,
        user_id=user_id,
    )
    session.add(db_search_history)
    session.commit()
    session.refresh(db_search_history)
    data = {
        "original_sequence": data_in.sequence,
        "reverse_complement_sequence": reverse_complement,
        "forward_strand_matches": forward_matches_with_color,
        "reverse_strand_matches": reverse_matches_with_color,
        "factors": found_factors,
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


def query_care(
    session: Session,
    data_in: QueryCareSearchIn,
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

    return FactorsListOut(data=db_factors, count=count)


async def motif_sampler(
    f_file: UploadFile = File(...),
    b_file: UploadFile = File(...),
    output_o: str = Form(...),
    output_m: str = Form(...),
    r: int | None = Form(100),
    s: int | None = Form(0),
    w: int | None = Form(8),
    n: int | None = Form(1),
    x: int | None = Form(1),
    M: int | None = Form(2),
    p: int | None = Form(None),
    Q: int | None = Form(100),
    z: int | None = Form(1),
) -> MotifSamplerResponse:
    # handle file upload
    f_file_path = await save_upload_file(f_file)
    b_file_path = await save_upload_file(b_file) if b_file else None

    parameters = {
        "r": r,
        "s": s,
        "w": w,
        "n": n,
        "x": x,
        "M": M,
        "p": p,
        "Q": Q,
        "z": z,
    }

    # try:
    motifs = await run_motif_sampler(
        f_file_path, b_file_path, output_o, output_m, **parameters
    )

    return MotifSamplerResponse(
        status="success",
        message="Motif sampler completed successfully.",
        results=motifs,
    )
    # except Exception as e:
    #     raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


async def save_upload_file(uploaded_file: UploadFile):
    # Create media_motifsampler directory if not exists
    save_dir = "media_motifsampler"
    os.makedirs(save_dir, exist_ok=True)

    file_path = os.path.join(save_dir, uploaded_file.filename)

    # Save file into media_motifsampler
    with open(file_path, "wb") as f:
        content = await uploaded_file.read()
        f.write(content)

    return file_path


async def run_motif_sampler(
    f_file_path: str,
    b_file_path: str | None = None,
    output_o: str = "output.txt",
    output_m: str = "output.mtrx",
    **parameters,
) -> list[str]:
    """
    Thực thi chương trình motif-sampler và trả về danh sách chuỗi consensus.

    Args:
        f_file_path: Đường dẫn đến file chứa chuỗi DNA (fasta).
        b_file_path: Đường dẫn đến file background genome (optional).
        output_o: Tên file output cho kết quả annotated instances.
        output_m: Tên file output cho kết quả PWM.
        **parameters: Các tham số khác cho motif-sampler.

    Returns:
        Danh sách các chuỗi consensus của motif được tìm thấy.
    """

    # Xây dựng command line
    command = ["motif-sampler", "-f", f_file_path]
    if b_file_path:
        command.extend(["-b", b_file_path])
    command.extend(["-o", output_o, "-m", output_m])
    for key, value in parameters.items():
        if value is not None:
            command.extend([f"-{key}", str(value)])

    # Thực thi command line
    process = await asyncio.create_subprocess_exec(
        *command, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await process.communicate()

    # Xử lý kết quả
    if process.returncode == 0:
        motifs = []
        for line in stdout.decode().splitlines():
            if line.startswith("#Consensus"):
                motif = line.split(":")[1].strip()
                motifs.append(motif)
        return motifs
    else:
        error_message = stderr.decode().strip()
        raise Exception(f"Motif sampler failed with error: {error_message}")
