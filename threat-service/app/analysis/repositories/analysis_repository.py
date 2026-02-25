"""Analysis repository — encapsula chamadas ao ORM."""

from __future__ import annotations

import random
import string
import uuid
from datetime import date, datetime, time, timezone
from pathlib import Path

from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from app.analysis.models import Analysis, AnalysisStatus
from app.config import get_settings


def _generate_analysis_code(prefix: str = "TMA", length: int = 8) -> str:
    """Gera código no formato prefixo + dígitos aleatórios (ex.: TMA-12345678)."""
    random_part = "".join(random.choices(string.digits, k=length))
    return f"{prefix}-{random_part}"


class AnalysisRepository:
    """Repository para operações de Analysis no banco."""

    def __init__(self, db: Session) -> None:
        self._db = db
        self._settings = get_settings()
        self._upload_dir = Path(self._settings.upload_dir)
        self._upload_dir.mkdir(parents=True, exist_ok=True)

    def _next_code(self) -> str:
        """Gera próximo código único (TMA-XXXXXXXX)."""
        max_attempts = 10
        for _ in range(max_attempts):
            code = _generate_analysis_code()
            existing = (
                self._db.execute(select(Analysis).where(Analysis.code == code).limit(1))
                .scalars()
                .first()
            )
            if not existing:
                return code
        raise RuntimeError("Could not generate unique analysis code")

    def _save_image(self, image_bytes: bytes, analysis_id: uuid.UUID) -> str:
        """Salva imagem em media/ e retorna nome do arquivo."""
        ext = ".png"
        if len(image_bytes) >= 8 and image_bytes[:8] == b"\x89PNG\r\n\x1a\n":
            ext = ".png"
        elif len(image_bytes) >= 12 and image_bytes[8:12] == b"WEBP":
            ext = ".webp"
        elif len(image_bytes) >= 2 and image_bytes[:2] == b"\xff\xd8":
            ext = ".jpg"
        filename = f"{analysis_id}{ext}"
        path = self._upload_dir / filename
        path.write_bytes(image_bytes)
        return filename

    def create(self, image_bytes: bytes, filename: str) -> Analysis:
        """Cria nova analysis com status EM_ABERTO."""
        analysis_id = uuid.uuid4()
        code = self._next_code()
        stored_filename = self._save_image(image_bytes, analysis_id)
        analysis = Analysis(
            id=analysis_id,
            code=code,
            image_path=stored_filename,
            status=AnalysisStatus.EM_ABERTO,
        )
        self._db.add(analysis)
        self._db.commit()
        self._db.refresh(analysis)
        return analysis

    def get_by_id(self, analysis_id: uuid.UUID) -> Analysis | None:
        """Busca analysis por ID."""
        return self._db.get(Analysis, analysis_id)

    def get_pending(self) -> Analysis | None:
        """Retorna uma analysis EM_ABERTO para processamento (FIFO)."""
        result = self._db.execute(
            select(Analysis)
            .where(Analysis.status == AnalysisStatus.EM_ABERTO)
            .order_by(Analysis.created_at)
            .limit(1)
        )
        return result.scalars().first()

    def list_all(
        self,
        status: AnalysisStatus | None = None,
        code_substring: str | None = None,
        created_at_from: date | None = None,
        created_at_to: date | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[Analysis]:
        """
        Lista analyses com filtros opcionais:
        - code_substring: parte do código (case insensitive)
        - status: combo de status
        - created_at_from / created_at_to: range de datas (sem horário, inclusivo)
        """
        q = select(Analysis).order_by(desc(Analysis.created_at))
        if status is not None:
            q = q.where(Analysis.status == status)
        if code_substring and code_substring.strip():
            q = q.where(Analysis.code.ilike(f"%{code_substring.strip()}%"))
        if created_at_from is not None:
            q = q.where(
                Analysis.created_at
                >= datetime.combine(created_at_from, time.min, tzinfo=timezone.utc)
            )
        if created_at_to is not None:
            q = q.where(
                Analysis.created_at
                <= datetime.combine(created_at_to, time.max, tzinfo=timezone.utc)
            )
        q = q.limit(limit).offset(offset)
        result = self._db.execute(q)
        return list(result.scalars().all())

    def update_status(
        self,
        analysis_id: uuid.UUID,
        status: AnalysisStatus,
        *,
        started_at: datetime | None = None,
        finished_at: datetime | None = None,
        result: dict | None = None,
        processing_logs: str | None = None,
        error_message: str | None = None,
    ) -> Analysis | None:
        """Atualiza status e campos relacionados."""
        analysis = self._db.get(Analysis, analysis_id)
        if not analysis:
            return None
        analysis.status = status
        if started_at is not None:
            analysis.started_at = started_at
        if finished_at is not None:
            analysis.finished_at = finished_at
        if result is not None:
            analysis.result = result
        if processing_logs is not None:
            analysis.processing_logs = processing_logs
        if error_message is not None:
            analysis.error_message = error_message
        self._db.commit()
        self._db.refresh(analysis)
        return analysis

    def mark_processing(
        self, analysis_id: uuid.UUID, *, started_at: datetime | None = None
    ) -> Analysis | None:
        """Marca análise como PROCESSANDO (início do processamento)."""
        return self.update_status(
            analysis_id,
            AnalysisStatus.PROCESSANDO,
            started_at=started_at,
        )

    def mark_failed(
        self,
        analysis_id: uuid.UUID,
        *,
        finished_at: datetime | None = None,
        error_message: str | None = None,
    ) -> Analysis | None:
        """Marca análise como FALHOU com mensagem de erro."""
        return self.update_status(
            analysis_id,
            AnalysisStatus.FALHOU,
            finished_at=finished_at,
            error_message=error_message,
        )

    def mark_analysed(
        self,
        analysis_id: uuid.UUID,
        *,
        finished_at: datetime | None = None,
        result: dict | None = None,
    ) -> Analysis | None:
        """Marca análise como ANALISADO com resultado."""
        return self.update_status(
            analysis_id,
            AnalysisStatus.ANALISADO,
            finished_at=finished_at,
            result=result,
        )

    def append_processing_log(self, analysis_id: uuid.UUID, log_line: str) -> bool:
        """Adiciona linha ao processing_logs."""
        analysis = self._db.get(Analysis, analysis_id)
        if not analysis:
            return False
        current = analysis.processing_logs or ""
        analysis.processing_logs = current + log_line + "\n"
        self._db.commit()
        return True

    def get_image_path(self, analysis_id: uuid.UUID) -> Path | None:
        """Retorna caminho completo da imagem."""
        analysis = self._db.get(Analysis, analysis_id)
        if not analysis:
            return None
        full_path = self._upload_dir / analysis.image_path
        if not full_path.exists():
            return None
        return full_path

    def delete(self, analysis_id: uuid.UUID) -> bool:
        """Remove a análise do banco e o arquivo de imagem do disco. Retorna True se existia e foi removida."""
        analysis = self._db.get(Analysis, analysis_id)
        if not analysis:
            return False
        image_path = self._upload_dir / analysis.image_path
        if image_path.exists():
            try:
                image_path.unlink()
            except OSError:
                pass
        self._db.delete(analysis)
        self._db.commit()
        return True
