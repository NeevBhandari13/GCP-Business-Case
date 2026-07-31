import logging
import os
import time
from contextlib import asynccontextmanager

import aiomysql
from fastapi import FastAPI, HTTPException
from google.cloud import secretmanager
from pydantic import BaseModel

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

_pool: aiomysql.Pool = None


def _fetch_secret(project_id: str, secret_id: str) -> str:
    """Pull a secret value from Secret Manager. Workload Identity supplies the credentials."""
    client = secretmanager.SecretManagerServiceClient()
    name = f"projects/{project_id}/secrets/{secret_id}/versions/latest"
    response = client.access_secret_version(request={"name": name})
    return response.payload.data.decode("utf-8")


async def _init_db(pool: aiomysql.Pool) -> None:
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute("""
                CREATE TABLE IF NOT EXISTS scoring_events (
                    id          INT AUTO_INCREMENT PRIMARY KEY,
                    patient_id  VARCHAR(255) NOT NULL,
                    clinic_id   VARCHAR(255) NOT NULL,
                    risk_score  FLOAT NOT NULL,
                    risk_tier   VARCHAR(10) NOT NULL,
                    scored_at   DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    INDEX idx_patient (patient_id)
                )
            """)
        await conn.commit()


@asynccontextmanager
async def lifespan(app: FastAPI):
    global _pool
    project_id = os.environ["GCP_PROJECT_ID"]
    secret_id = os.environ.get("DB_SECRET_ID", "blissey-db-password")

    db_password = _fetch_secret(project_id, secret_id)

    _pool = await aiomysql.create_pool(
        host=os.environ.get("DB_HOST", "127.0.0.1"),
        port=int(os.environ.get("DB_PORT", "3306")),
        db=os.environ.get("DB_NAME", "blissey"),
        user=os.environ.get("DB_USER", "blissey_app"),
        password=db_password,
        minsize=2,
        maxsize=10,
        autocommit=False,
    )
    await _init_db(_pool)
    logger.info("Database pool ready")
    yield
    _pool.close()
    await _pool.wait_closed()


app = FastAPI(title="Blissey Risk Scoring Service", lifespan=lifespan)


# ---------------------------------------------------------------------------
# Request / response models
# ---------------------------------------------------------------------------

class PatientRecord(BaseModel):
    patient_id: str
    clinic_id: str
    age: int                    # 0-120
    num_conditions: int         # chronic conditions on record
    num_medications: int        # active prescriptions
    last_visit_days_ago: int    # days since last clinic contact


class RiskScore(BaseModel):
    patient_id: str
    clinic_id: str
    risk_score: float   # 0.0 - 1.0
    risk_tier: str      # "low" | "medium" | "high"
    scored_at: float    # unix timestamp


# ---------------------------------------------------------------------------
# Toy scoring model
# ---------------------------------------------------------------------------

def _compute_risk(r: PatientRecord) -> float:
    # Intentionally simple — the platform story matters, not ML sophistication.
    return round(
        min(r.age, 100) / 100 * 0.20
        + min(r.num_conditions, 10) / 10 * 0.40
        + min(r.num_medications, 20) / 20 * 0.25
        + min(r.last_visit_days_ago, 365) / 365 * 0.15,
        3,
    )


def _tier(score: float) -> str:
    if score < 0.33:
        return "low"
    if score < 0.66:
        return "medium"
    return "high"


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/score", response_model=RiskScore)
async def score(record: PatientRecord):
    risk_score = _compute_risk(record)
    tier = _tier(risk_score)

    async with _pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                """
                INSERT INTO scoring_events (patient_id, clinic_id, risk_score, risk_tier)
                VALUES (%s, %s, %s, %s)
                """,
                (record.patient_id, record.clinic_id, risk_score, tier),
            )
        await conn.commit()

    logger.info(
        "scored patient=%s clinic=%s score=%s tier=%s",
        record.patient_id, record.clinic_id, risk_score, tier,
    )
    return RiskScore(
        patient_id=record.patient_id,
        clinic_id=record.clinic_id,
        risk_score=risk_score,
        risk_tier=tier,
        scored_at=time.time(),
    )


@app.get("/scores/{patient_id}")
async def get_scores(patient_id: str):
    async with _pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cur:
            await cur.execute(
                """
                SELECT patient_id, clinic_id, risk_score, risk_tier, scored_at
                FROM scoring_events
                WHERE patient_id = %s
                ORDER BY scored_at DESC
                LIMIT 20
                """,
                (patient_id,),
            )
            rows = await cur.fetchall()
    if not rows:
        raise HTTPException(status_code=404, detail="No scores found for this patient")
    return rows
