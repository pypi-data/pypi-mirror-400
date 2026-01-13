import datetime
import time
from dataclasses import dataclass
from flask import request, current_app as app

from opentakserver.functions import iso8601_string_from_datetime
from opentakserver.extensions import db, logger
from sqlalchemy import Integer, String, Boolean, JSON, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from opentakserver.models.MissionRole import MissionRole


@dataclass
class Report(db.Model):
    __tablename__ = "reports"

    id: Mapped[str] = mapped_column(String(255), primary_key=True)
    type: Mapped[str] = mapped_column(String(255), nullable=True)
    user_callsign: Mapped[str] = mapped_column(String(255), ForeignKey("user.username", ondelete="CASCADE"), nullable=True)
    user_description: Mapped[str] = mapped_column(String(255), nullable=True)
    date_time: Mapped[DateTime] = mapped_column(DateTime, nullable=True)
    date_time_description: Mapped[str] = mapped_column(String(255), nullable=True)
    : Mapped[str] = mapped_column(String(255), nullable=True)
