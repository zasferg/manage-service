from sqlalchemy.ext.asyncio import AsyncSession
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
