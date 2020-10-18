from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Text

Base = declarative_base()

class PredictionEntry(Base):
    __tablename__ = 'predictions'
    uuid = Column(String(50),primary_key=True)
    img = Column(String(1000000))
    prediction = Column(String(50))

    def __repr__(self):
        return "<PredictionEntry(uuid='%s', img='%s', prediction='%s')>" % (
                                self.uuid, self.img, self.prediction)