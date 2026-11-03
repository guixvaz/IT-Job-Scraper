from sqlmodel import Field, SQLModel, create_engine, Session

class JobListing(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    job_id: str = Field(index=True, unique=True) # e.g., "jobsch_12345"
    title: str
    company: str
    location: str
    workload: str
    url: str
    platform: str

# Create local SQLite database
sqlite_file_name = "jobs.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"
engine = create_engine(sqlite_url, echo=True) # echo=True prints SQL commands to terminal for debugging

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

if __name__ == "__main__":
    print("Initializing database...")
    create_db_and_tables()
    print("Database created successfully.")