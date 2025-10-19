from sqladmin import ModelView
from sqladmin.filters import (
    AllUniqueStringValuesFilter,
    ForeignKeyFilter,
    BooleanFilter,
)
from app.infrastructure.database.models.models import *


class UserAdmin(ModelView, model=User):
    column_list = [
        User.id,
        User.email,
        User.role,
        User.company,
        User.performed_tasks,
        User.authored_tasks,
        User.meetings,
    ]

    form_columns = ["email", "password", "role"]

    column_filters = [
        AllUniqueStringValuesFilter(User.role, title="По ролям"),
        ForeignKeyFilter(User.company_id, Company.name, title="По компании"),
    ]

    column_searchable_list = [
        User.email,
    ]


class TokenAdmin(ModelView, model=Token):
    column_list = [Token.user, Token.refresh_token]


class CompanyAdmin(ModelView, model=Company):
    column_list = [Company.id, Company.name]

    form_columns = ["name"]

    column_searchable_list = [
        Company.name,
        Company.id,
    ]


class TaskAdmin(ModelView, model=Task):
    column_list = [
        Task.id,
        Task.description,
        Task.status,
        Task.deadline,
        Task.mark,
        Task.perform_user,
        Task.author,
        Task.company,
        Task.comments,
    ]

    form_columns = [
        "description",
        "deadline",
        "company",
    ]

    column_filters = [
        AllUniqueStringValuesFilter(Task.status, title="Статус"),
        ForeignKeyFilter(Task.perform_user_id, User.email, title="Исполнитель"),
        ForeignKeyFilter(Task.author_id, User.email, title="Автор"),
    ]

    column_searchable_list = [Task.id]


class MeetingsAdmin(ModelView, model=Meetings):
    column_list = [
        Meetings.id,
        Meetings.description,
        Meetings.user,
        Meetings.meeting_starttime,
        Meetings.meeting_endtime,
        Meetings.is_finished,
        Meetings.is_cancelled,
    ]

    form_column = [
        "description",
        "user",
        "meeting_starttime",
        "meeting_endtime",
    ]

    column_filters = [
        BooleanFilter(Meetings.is_finished, title="Завершены"),
        BooleanFilter(Meetings.is_cancelled, title="Отменены"),
        AllUniqueStringValuesFilter(Meetings.meeting_starttime, title="Начало"),
        AllUniqueStringValuesFilter(Meetings.meeting_endtime, title="Окончание"),
    ]

    column_searchable_list = [Meetings.id]
