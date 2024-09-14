import os
import subprocess
from fastapi import File, Form, HTTPException, UploadFile, status
from sqlalchemy import func
from sqlmodel import Session, select

from models.computational_motif import ComputationalMotif, ComputationalMotifListOut
from models.factors import FactorsIn, MotifSamplerResponse, Factors
from models.base import Message
from core.config import settings
from utils import random_color


async def motif_sampler(
    session,
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
    is_biologist_action: bool = False,
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

    if is_biologist_action:
        try:
            motifs = await run_motif_sampler(
                f_file_path, b_file_path, output_o, output_m, **parameters
            )
            # save to computational_motif table
            motif_in = []
            for motif in motifs:
                db_computational_motif = ComputationalMotif(sequences=motif)
                motif_in.append(db_computational_motif)
            session.add_all(motif_in)
            session.commit()
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e),
            )

    return MotifSamplerResponse(
        status="success",
        message="Motif sampler completed successfully.",
        results=motifs,
    )


async def save_upload_file(uploaded_file: UploadFile):
    # Create media_motifsampler directory if not exists
    save_dir = "./app/media_motifsampler"
    os.makedirs(save_dir, exist_ok=True)

    file_path = os.path.join(save_dir, uploaded_file.filename)

    # Save file into media_motifsampler
    with open(file_path, "wb") as f:
        content = await uploaded_file.read()
        f.write(content)

    return uploaded_file.filename


async def run_motif_sampler(
    f_file_path: str,
    b_file_path: str | None = None,
    output_o: str = "output.txt",
    output_m: str = "output.mtrx",
    **parameters,
) -> list[str]:
    """
    Runs the motif sampler tool with the given parameters.

    Args:
        f_file_path (str): The file path of the input file.
        b_file_path (str, optional): The file path of the background file. Defaults to None.
        output_o (str, optional): The output file path for the motifs. Defaults to "output.txt".
        output_m (str, optional): The output file path for the motif matrix. Defaults to "output.mtrx".
        **parameters: Additional parameters to be passed to the motif sampler tool.

    Returns:
        list[str]: A list of motifs extracted by the motif sampler tool.

    Raises:
        Exception: If the motif sampler fails with an error.

    """
    # Construct command line
    command = [
        "cd",
        "./app/media_motifsampler",
        "&&",
        "./motif-sampler",
        "-f",
        f_file_path,
    ]
    if b_file_path:
        command.extend(["-b", b_file_path])
    command.extend(["-o", output_o, "-m", output_m])
    for key, value in parameters.items():
        if value is not None:
            command.extend([f"-{key}", str(value)])

    # Execute command line
    command = " ".join(command)
    process = subprocess.run(command, capture_output=True, text=True, shell=True)

    # Handle results
    if process.returncode == 0:
        path_result = f"./app/media_motifsampler/{output_m}"
        with open(path_result, "r") as f:
            motifs = []
            for line in f:
                if line.startswith("#Consensus"):
                    motif = line.split("=")[1].strip()  # Keep only the sequence part
                    motifs.append(motif)
        return motifs
    else:
        error_message = process.stderr.strip()
        raise Exception(f"Motif sampler failed with error: {error_message}")


def read_computational_motifs(
    session: Session, skip: int = 0, limit: int = settings.RECORD_LIMIT
) -> ComputationalMotifListOut:
    count = session.exec(
        select(func.count(ComputationalMotif.id)).select_from(ComputationalMotif)
    ).one()
    db_computational_motifs = session.exec(
        select(ComputationalMotif).offset(skip).limit(limit)
    ).all()

    return ComputationalMotifListOut(data=db_computational_motifs, count=count)


def read_computational_motif(session: Session, motif_id: int) -> ComputationalMotif:
    db_computational_motif = session.get(ComputationalMotif, motif_id)
    if db_computational_motif is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Computational motif not found",
        )

    return db_computational_motif


def delete_computational_motif(session: Session, motif_id: int) -> Message:
    db_computational_motif = session.get(ComputationalMotif, motif_id)
    if db_computational_motif is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Computational motif not found",
        )

    session.delete(db_computational_motif)
    session.commit()

    return Message(status_code=status.HTTP_200_OK, message="Item deleted")


def validate_computational_motif(
    session: Session, motif_id: int, data_in: FactorsIn
) -> Message:
    db_computational_motif = session.get(ComputationalMotif, motif_id)
    if db_computational_motif is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Computational motif not found",
        )

    # add factors to db
    color = random_color()
    data_in = {
        **data_in.model_dump(),
        "color": color,
    }
    db_factor = Factors(**data_in)
    session.add(db_factor)
    session.flush()

    # remove computational motif
    session.delete(db_computational_motif)
    session.commit()

    return Message(
        status_code=status.HTTP_200_OK, message="Validation completed successfully."
    )
