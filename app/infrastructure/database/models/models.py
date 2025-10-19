from uuid import UUID, uuid4
from datetime import datetime
from sqlalchemy import (
    String,
    ForeignKey,
    Text,
    Integer,
    DateTime,
    Boolean,
    func,
    Table,
    Column,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship, DeclarativeBase
from app.core.enums import RolesEnum, TaskStatuses


class Base(DeclarativeBase):

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    created: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_on: Mapped[datetime] = mapped_column(
        DateTime(), server_default=func.now(), onupdate=func.now()
    )


UserMeetingRelation = Table(
    "user_meeting_relations",
    Base.metadata,
    Column("user_id", ForeignKey("user_accounts.id"), primary_key=True),
    Column("meeting_id", ForeignKey("meetings.id"), primary_key=True),
)


class User(Base):
    __tablename__ = "user_accounts"

    email: Mapped[str] = mapped_column(String, nullable=False)
    password: Mapped[str] = mapped_column(String, nullable=False)
    role: Mapped[str] = mapped_column(String, nullable=True, default=RolesEnum.USER)
    company_id: Mapped[UUID] = mapped_column(
        ForeignKey("companies.id"),
        nullable=True,
    )

    company: Mapped["Company"] = relationship(back_populates="users", lazy="selectin")
    performed_tasks: Mapped[list["Task"]] = relationship(
        back_populates="perform_user", foreign_keys="[Task.perform_user_id]"
    )
    authored_tasks: Mapped[list["Task"]] = relationship(
        back_populates="author", foreign_keys="[Task.author_id]"
    )
    meetings: Mapped[list["Meetings"]] = relationship(
        secondary="user_meeting_relations", back_populates="user"
    )
    token: Mapped["Token"] = relationship(back_populates="user", uselist=False)

    def __str__(self):
        return self.email


class Token(Base):
    __tablename__ = "tokens"

    refresh_token: Mapped[str] = mapped_column(
        Text, nullable=False, unique=True, index=True
    )
    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("user_accounts.id"),
    )
    user: Mapped["User"] = relationship(back_populates="token")


class Company(Base):
    __tablename__ = "companies"

    name: Mapped[str] = mapped_column(String, nullable=True)

    users: Mapped[list["User"]] = relationship(
        back_populates="company", lazy="selectin"
    )
    tasks: Mapped[list["Task"]] = relationship(back_populates="company")

    def __str__(self):
        return self.name


class Task(Base):
    __tablename__ = "tasks"

    description: Mapped[str] = mapped_column(String, nullable=False)
    status: Mapped[str] = mapped_column(
        String, nullable=False, default=TaskStatuses.OPENED
    )
    deadline: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    company_id: Mapped[UUID] = mapped_column(ForeignKey("companies.id"))
    perform_user_id: Mapped[UUID] = mapped_column(
        ForeignKey("user_accounts.id"), nullable=True
    )
    author_id: Mapped[UUID] = mapped_column(
        ForeignKey("user_accounts.id"), nullable=False
    )

    comments: Mapped[list["Comments"]] = relationship(back_populates="tasks")
    company: Mapped["Company"] = relationship(back_populates="tasks")
    perform_user: Mapped["User"] = relationship(
        back_populates="performed_tasks", foreign_keys=[perform_user_id]
    )
    author: Mapped["User"] = relationship(
        back_populates="authored_tasks", foreign_keys=[author_id]
    )
    mark: Mapped["Evaluation"] = relationship(back_populates="tasks", lazy="selectin")

    def __str__(self):
        return f"Задача: {self.description}"


class Evaluation(Base):
    __tablename__ = "evaluations"

    mark: Mapped[int] = mapped_column(Integer, nullable=True)
    task_id: Mapped[UUID] = mapped_column(ForeignKey("tasks.id"))

    tasks: Mapped["Task"] = relationship(back_populates="mark")

    def __str__(
        self,
    ):
        return f"Оценка задания {self.task_id} - {self.mark}"


class Comments(Base):
    __tablename__ = "comments"

    parent_id: Mapped[UUID] = mapped_column(ForeignKey("comments.id"), nullable=True)
    text: Mapped[str] = mapped_column(String, nullable=False)
    from_user_id: Mapped[UUID] = mapped_column(ForeignKey("user_accounts.id"))
    to_user_id: Mapped[UUID] = mapped_column(ForeignKey("user_accounts.id"))
    task_id: Mapped[int] = mapped_column(ForeignKey("tasks.id"), nullable=False)
    tasks: Mapped["Task"] = relationship(back_populates="comments")
    from_user: Mapped["User"] = relationship(foreign_keys=[from_user_id])
    to_user: Mapped["User"] = relationship(foreign_keys=[to_user_id])

    def __str__(self):
        return self.text


class Meetings(Base):

    __tablename__ = "meetings"

    description: Mapped[str] = mapped_column(String, nullable=False)
    meeting_starttime: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    meeting_endtime: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    is_finished: Mapped[bool] = mapped_column(Boolean, default=False)
    is_cancelled: Mapped[bool] = mapped_column(Boolean, default=False)
    user: Mapped[list["User"]] = relationship(
        secondary="user_meeting_relations", back_populates="meetings", lazy="selectin"
    )

    def __str__(self):
        return self.description
