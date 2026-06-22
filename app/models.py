"""
Ma'lumotlar bazasi modellari — prognozlar arxivi.
SQLite + Flask-SQLAlchemy
"""
import os
import json
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Forecast(db.Model):
    """Bitta prognoz yozuvi (3 kunlik to'plam)."""
    __tablename__ = "forecasts"

    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    created_by = db.Column(db.String(100), default="sinoptik")

    # 3 kunlik ma'lumot (JSON)
    day1_date = db.Column(db.String(10))  # "2026-06-19"
    day2_date = db.Column(db.String(10))
    day3_date = db.Column(db.String(10))

    day1_data = db.Column(db.Text)  # JSON: {cities: {...}, comment: "..."}
    day2_data = db.Column(db.Text)
    day3_data = db.Column(db.Text)

    # Generatsiya natijalari
    image1_path = db.Column(db.String(200))
    image2_path = db.Column(db.String(200))
    image3_path = db.Column(db.String(200))

    # Holat
    status = db.Column(db.String(20), default="draft")  # draft, published, archived

    def set_day_data(self, day_index, data):
        """Kunlik ma'lumotni JSON sifatida saqlash."""
        json_str = json.dumps(data, ensure_ascii=False)
        if day_index == 0:
            self.day1_data = json_str
            self.day1_date = data.get("date", "")
        elif day_index == 1:
            self.day2_data = json_str
            self.day2_date = data.get("date", "")
        elif day_index == 2:
            self.day3_data = json_str
            self.day3_date = data.get("date", "")

    def get_day_data(self, day_index):
        """Kunlik ma'lumotni dict sifatida olish."""
        raw = [self.day1_data, self.day2_data, self.day3_data][day_index]
        if raw:
            return json.loads(raw)
        return None

    def to_dict(self):
        return {
            "id": self.id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "created_by": self.created_by,
            "day1_date": self.day1_date,
            "day2_date": self.day2_date,
            "day3_date": self.day3_date,
            "status": self.status,
            "images": [self.image1_path, self.image2_path, self.image3_path],
        }


def init_db(app):
    """Ma'lumotlar bazasini Flask ilovaga ulash."""
    # Render'da /tmp yozish mumkin, app root'da esa yo'q
    import tempfile
    basedir = app.root_path
    data_dir = os.path.join(basedir, "data")
    try:
        os.makedirs(data_dir, exist_ok=True)
        # Test yozish
        test_file = os.path.join(data_dir, ".write_test")
        with open(test_file, "w") as f:
            f.write("ok")
        os.remove(test_file)
        db_path = f"sqlite:///{data_dir}/forecasts.db"
    except (OSError, PermissionError):
        # Fallback: /tmp ga yozish
        db_path = f"sqlite:////tmp/forecasts.db"

    app.config["SQLALCHEMY_DATABASE_URI"] = db_path
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.init_app(app)
    with app.app_context():
        db.create_all()
