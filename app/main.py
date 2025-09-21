from fastapi import FastAPI
import uvicorn
from presentation.authentication import auth
from presentation.calendar import calendar
from presentation.companies import companies
from presentation.marks import marks
from presentation.meetings import meetings
from presentation.tasks import tasks
from presentation.users import users
from infrastructure.database.session import engine
from sqladmin import Admin
from infrastructure.admin.sqladmin import (
    UserAdmin,
    TokenAdmin,
    CompanyAdmin,
    TaskAdmin,
    MeetingsAdmin,
)

app = FastAPI()

app.include_router(auth)
app.include_router(users)
app.include_router(companies)
app.include_router(tasks)
app.include_router(marks)
app.include_router(meetings)
app.include_router(calendar)

admin = Admin(app, engine)

admin.add_view(UserAdmin)
admin.add_view(TokenAdmin)
admin.add_view(CompanyAdmin)
admin.add_view(TaskAdmin)
admin.add_view(MeetingsAdmin)


if __name__ == "__main__":
    uvicorn.run(app="app/main:app", host="localhost", port=8080, reload=True)
