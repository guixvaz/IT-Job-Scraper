from nicegui import ui
from sqlmodel import Session, select
from src.db import engine, JobListing

def fetch_jobs():
    with Session(engine) as session:
        # Fetch all jobs, ordered by newest first
        statement = select(JobListing).order_by(JobListing.id.desc())
        return session.exec(statement).all()

@ui.page('/')
def index_page():
    # Header
    with ui.row().classes('w-full items-center justify-between p-4 bg-slate-800 text-white shadow-lg'):
        ui.label('IT Student Job Dashboard').classes('text-2xl font-bold')
        ui.button('Refresh', on_click=lambda: ui.navigate.to('/')).classes('bg-blue-600')

    # Job Grid
    with ui.row().classes('w-full flex-wrap gap-6 p-6 bg-slate-50 min-h-screen'):
        jobs = fetch_jobs()
        
        if not jobs:
            ui.label('No jobs found in the database. Run the scraper first.').classes('text-lg text-slate-500')
            
        for job in jobs:
            # Tailwind styled card for each job
            with ui.card().classes('w-80 shadow-md hover:shadow-xl transition-shadow duration-200 border border-slate-200'):
                ui.label(job.title).classes('text-xl font-bold text-slate-800 line-clamp-2')
                ui.label(job.company).classes('text-md font-semibold text-blue-600 mt-1')
                
                ui.separator().classes('my-2')
                
                with ui.row().classes('w-full justify-between items-center text-sm text-slate-600'):
                    with ui.row().classes('items-center gap-1'):
                        ui.icon('place', size='sm')
                        ui.label(job.location)
                    with ui.row().classes('items-center gap-1'):
                        ui.icon('schedule', size='sm')
                        ui.label(job.workload).classes('font-medium')
                
                with ui.row().classes('w-full justify-between items-center mt-4'):
                    ui.label(job.platform).classes('text-xs bg-slate-200 px-2 py-1 rounded text-slate-700 uppercase font-bold')
                    ui.link('View Posting', job.url, new_tab=True).classes('bg-blue-600 text-white px-4 py-2 rounded shadow hover:bg-blue-700 no-underline text-sm font-medium')

def run_dashboard():
    ui.run(title="Job Dashboard", port=8080)