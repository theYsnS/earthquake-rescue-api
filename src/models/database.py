import math
import sqlite3
from datetime import datetime
from typing import Optional


def haversine(lat1, lon1, lat2, lon2):
    R = 6371
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


class Database:
    def __init__(self, db_path: str = 'rescue.db'):
        self.db_path = db_path
        self._init_db()

    def _connect(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        with self._connect() as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS reports (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    latitude REAL NOT NULL, longitude REAL NOT NULL,
                    severity TEXT DEFAULT 'high', status TEXT DEFAULT 'pending',
                    description TEXT DEFAULT '', num_trapped INTEGER DEFAULT 1,
                    contact_phone TEXT DEFAULT '', assigned_team_id INTEGER,
                    created_at TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS teams (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL, members INTEGER NOT NULL,
                    specialization TEXT DEFAULT '',
                    latitude REAL DEFAULT 0, longitude REAL DEFAULT 0,
                    is_available INTEGER DEFAULT 1, current_assignment INTEGER);
                CREATE TABLE IF NOT EXISTS devices (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    device_id TEXT UNIQUE NOT NULL, device_type TEXT NOT NULL,
                    latitude REAL DEFAULT 0, longitude REAL DEFAULT 0,
                    last_seen TEXT, is_active INTEGER DEFAULT 1);
                CREATE TABLE IF NOT EXISTS sensor_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    device_id TEXT NOT NULL, vibration REAL, gas_level REAL,
                    sound_level REAL, temperature REAL, timestamp TEXT NOT NULL);
            """)

    def create_report(self, data: dict) -> dict:
        now = datetime.now().isoformat()
        with self._connect() as conn:
            cur = conn.execute(
                'INSERT INTO reports (latitude,longitude,severity,description,num_trapped,contact_phone,created_at) VALUES (?,?,?,?,?,?,?)',
                (data['latitude'], data['longitude'], data['severity'], data.get('description',''), data.get('num_trapped',1), data.get('contact_phone',''), now))
            return {**data, 'id': cur.lastrowid, 'status': 'pending', 'created_at': now}

    def get_reports(self, status=None):
        with self._connect() as conn:
            if status:
                rows = conn.execute('SELECT * FROM reports WHERE status=? ORDER BY created_at DESC', (status,)).fetchall()
            else:
                rows = conn.execute('SELECT * FROM reports ORDER BY created_at DESC').fetchall()
            return [dict(r) for r in rows]

    def update_report_status(self, report_id, status):
        with self._connect() as conn:
            return conn.execute('UPDATE reports SET status=? WHERE id=?', (status, report_id)).rowcount > 0

    def get_nearby_reports(self, lat, lon, radius_km=10):
        reports = self.get_reports()
        nearby = []
        for r in reports:
            dist = haversine(lat, lon, r['latitude'], r['longitude'])
            if dist <= radius_km:
                r['distance_km'] = round(dist, 2)
                nearby.append(r)
        return sorted(nearby, key=lambda x: x['distance_km'])

    def create_team(self, data):
        with self._connect() as conn:
            cur = conn.execute('INSERT INTO teams (name,members,specialization,latitude,longitude) VALUES (?,?,?,?,?)',
                (data['name'], data['members'], data.get('specialization',''), data.get('latitude',0), data.get('longitude',0)))
            return {**data, 'id': cur.lastrowid, 'is_available': True}

    def get_teams(self, available_only=False):
        with self._connect() as conn:
            q = 'SELECT * FROM teams'
            if available_only: q += ' WHERE is_available=1'
            return [dict(r) for r in conn.execute(q).fetchall()]

    def update_team_location(self, team_id, lat, lon):
        with self._connect() as conn:
            return conn.execute('UPDATE teams SET latitude=?,longitude=? WHERE id=?', (lat, lon, team_id)).rowcount > 0

    def assign_team(self, team_id, report_id):
        with self._connect() as conn:
            conn.execute('UPDATE teams SET is_available=0,current_assignment=? WHERE id=?', (report_id, team_id))
            conn.execute('UPDATE reports SET assigned_team_id=?,status="in_progress" WHERE id=?', (team_id, report_id))
            return True

    def register_device(self, data):
        now = datetime.now().isoformat()
        with self._connect() as conn:
            conn.execute('INSERT OR REPLACE INTO devices (device_id,device_type,latitude,longitude,last_seen,is_active) VALUES (?,?,?,?,?,1)',
                (data['device_id'], data['device_type'], data.get('latitude',0), data.get('longitude',0), now))
            return {**data, 'last_seen': now, 'is_active': True}

    def add_sensor_data(self, device_id, data):
        now = data.get('timestamp', datetime.now().isoformat())
        with self._connect() as conn:
            conn.execute('INSERT INTO sensor_data (device_id,vibration,gas_level,sound_level,temperature,timestamp) VALUES (?,?,?,?,?,?)',
                (device_id, data.get('vibration'), data.get('gas_level'), data.get('sound_level'), data.get('temperature'), now))

    def get_stats(self):
        with self._connect() as conn:
            return {
                'total_reports': conn.execute('SELECT COUNT(*) FROM reports').fetchone()[0],
                'pending': conn.execute('SELECT COUNT(*) FROM reports WHERE status="pending"').fetchone()[0],
                'in_progress': conn.execute('SELECT COUNT(*) FROM reports WHERE status="in_progress"').fetchone()[0],
                'rescued': conn.execute('SELECT COUNT(*) FROM reports WHERE status="rescued"').fetchone()[0],
                'total_teams': conn.execute('SELECT COUNT(*) FROM teams').fetchone()[0],
                'available_teams': conn.execute('SELECT COUNT(*) FROM teams WHERE is_available=1').fetchone()[0],
            }
