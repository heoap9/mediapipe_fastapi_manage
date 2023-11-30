
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, String, Integer
from sqlalchemy.ext.declarative import declarative_base

import time
import cv2





SQLALCHEMY_DATABASE_URL = "sqlite:///./myapi.db"

DATABASE_URL = "sqlite:///./myapi.db"
Base = declarative_base()
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class FileList(Base):
    __tablename__ = 'filelist'
    index = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(String, nullable=False)
    time = Column(String, nullable=False)
    duration = Column(Integer)
    filename = Column(String)


class AdminList(Base):
    __tablename__ = 'adminlist'
    index = Column(Integer, primary_key=True, autoincrement=True)
    id = Column(String)
    pwd = Column(String)
    phone = Column(Integer)



def file_transfor_db(filename):
    cap = cv2.VideoCapture(filename)
    frame_count = cap.get(cv2.CAP_PROP_FRAME_COUNT)
    fps = cap.get(cv2.CAP_PROP_FPS)
    duration = int(frame_count / fps)
    cap.release()
    video = FileList(date=time.strftime("%Y_%m_%d"), time=time.strftime("%H:%M"),
                     filename=filename, duration=duration)
    db = SessionLocal()
    db.add(video)
    db.commit()
    db.close()



