from infrastructure.repositories.calendar import CalendarRepository
from infrastructure.repositories.tasks import TaskRepository
from infrastructure.repositories.meetings import MeetingRepository
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
import csv
from io import StringIO


class CalendarService:

    def __init__(self, session: AsyncSession):
        self.session = session

    async def convert_to_csv(self, events_data):
        output = StringIO()
        writer = csv.writer(output)
        writer.writerow(["ID", "Описание", "Дата", "Тип"])

        for event in events_data:
            writer.writerow(
                [
                    str(event[0]),
                    event[1],
                    event[2],
                    event[3],
                ]
            )

        csv_content = output.getvalue()
        output.close()

        return csv_content
