from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from app.presentation.authentication import auth
from app.presentation.calendar import calendar
from app.presentation.companies import companies
from app.presentation.marks import marks
from app.presentation.meetings import meetings
from app.presentation.tasks import tasks
from app.presentation.users import users
from app.infrastructure.database.session import engine
from sqladmin import Admin
from app.infrastructure.admin.auth import DBAuth
from app.infrastructure.admin.sqladmin import (
    UserAdmin,
    TokenAdmin,
    CompanyAdmin,
    TaskAdmin,
    MeetingsAdmin,
)
from app.core.config import settings
import os
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.join(BASE_DIR, "../frontend")

app = FastAPI()

app.include_router(auth)
app.include_router(users)
app.include_router(companies)
app.include_router(tasks)
app.include_router(marks)
app.include_router(meetings)
app.include_router(calendar)

admin = Admin(
    app=app,
    engine=engine,
    authentication_backend=DBAuth(secret_key=settings.SECRET_KEY_FOR_ADMIN),
)

admin.add_view(UserAdmin)
admin.add_view(TokenAdmin)
admin.add_view(CompanyAdmin)
admin.add_view(TaskAdmin)
admin.add_view(MeetingsAdmin)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True
)

app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")

if __name__ == "__main__":
    uvicorn.run(app="app/main:app", host="localhost", port=8080, reload=True)
