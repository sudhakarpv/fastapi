from typing import List
from datetime import datetime, date
import databases
import sqlalchemy
from fastapi import FastAPI
from pydantic import BaseModel
from pydantic.fields import Optional, Field

DATABASE_URL = "sqlite:///./jobs.db"

database = databases.Database(DATABASE_URL)

metadata = sqlalchemy.MetaData()

jobs = sqlalchemy.Table(
    "jobs",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("title", sqlalchemy.String),
    sqlalchemy.Column("description", sqlalchemy.String),
    sqlalchemy.Column("applied", sqlalchemy.Boolean),
    sqlalchemy.Column("experience", sqlalchemy.Integer),
    sqlalchemy.Column("lastdate", sqlalchemy.Integer),
    sqlalchemy.Column("created", sqlalchemy.DateTime),
)

engine = sqlalchemy.create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)
metadata.create_all(engine)


class Jobs(BaseModel):
    id: int
    title: str
    description: str
    experience: int
    lastdate: Optional[date]
    applied: Optional[bool]
    created: Optional[datetime]


app = FastAPI()


@app.on_event("startup")
async def startup():
    await database.connect()


@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()


@app.get("/jobs/", response_model=List[Jobs])
async def list_jobs():
    query = jobs.select()
    return await database.fetch_all(query)


@app.post("/jobs/", response_model=Jobs)
async def create_job(job: Jobs):
    query = jobs.insert().values(title=job.title, description=job.description, applied=False, experience=job.experience,
                                 lastdate=job.lastdate, created=datetime.now())
    last_record_id = await database.execute(query)
    return {**job.dict(), "id": last_record_id}


@app.delete("/jobs/{job_id}/")
async def delete_job(job_id: int):
    query = jobs.delete().where(jobs.c.id == job_id)
    await database.execute(query)
    return {"message": "Deleted successfully!"}


@app.put("/job/{job_id}/", response_model=Jobs)
async def update_job(job_id: int, payload: Jobs):
    query = jobs.update().where(jobs.c.id == job_id).values(title=payload.title, description=payload.description,
                                                            experience=payload.experience, lastdate=payload.lastdate,
                                                            applied=False)
    await database.execute(query)
    return {**payload.dict(), "id": job_id}


@app.put("/job/{job_id}/apply", response_model=Jobs)
async def apply_job(job_id: int, payload: Jobs):
    query = jobs.update().where(jobs.c.id == job_id).values(title=payload.title, description=payload.description,
                                                            experience=payload.experience, lastdate=payload.lastdate,
                                                            applied=True)
    await database.execute(query)
    return {**payload.dict(), "id": job_id}
