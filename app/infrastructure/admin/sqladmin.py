from sqladmin import ModelView
from infrastructure.database.models.models import *


class UserAdmin(ModelView, model=User):
    column_list = [User.email, User.role, User.company, User.tasks, User.meetings]


class TokenAdmin(ModelView, model=Token):
    column_list = [Token.user, Token.refresh_token]


class CompanyAdmin(ModelView, model=Company):
    column_list = [Company.name]


class TaskAdmin(ModelView, model=Task):
    column_list = [
        Task.description,
        Task.status,
        Task.deadline,
        Task.mark,
        Task.user,
        Task.company,
        Task.comments,
    ]


class MeetingsAdmin(ModelView, model=Meetings):
    column_list = [
        Meetings.description,
        Meetings.user,
        Meetings.meeting_starttime,
        Meetings.meeting_endtime,
        Meetings.is_finished,
        Meetings.is_cancelled,
    ]
