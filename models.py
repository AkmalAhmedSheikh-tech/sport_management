from flask_sqlalchemy import SQLAlchemy
from utils import utcnow

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.BigInteger().with_variant(db.Integer, "sqlite"), primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(
        db.Enum('admin', 'manager', 'viewer', name='user_roles'),
        nullable=False,
        default='manager'
    )
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=utcnow)
    last_login = db.Column(db.DateTime, nullable=True)

    def __repr__(self):
        return f"<User {self.username}>"

class Event(db.Model):
    __tablename__ = 'events'

    id = db.Column(db.BigInteger().with_variant(db.Integer, "sqlite"), primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    slug = db.Column(db.String(150), nullable=False, unique=True)
    description = db.Column(db.Text)
    sport_type = db.Column(db.String(50), default='football')
    season = db.Column(db.String(50))
    is_template = db.Column(db.Boolean, default=False)
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    created_by = db.Column(db.BigInteger, db.ForeignKey('users.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=utcnow)

    # all fixtures in this event: event.fixtures
    fixtures = db.relationship(
        "Fixture",
        back_populates="event",
        lazy="dynamic",
        passive_deletes=True
    )

    def __repr__(self):
        return f"<Event {self.name}>"

class Team(db.Model):
    __tablename__ = 'teams'

    id = db.Column(db.BigInteger().with_variant(db.Integer, "sqlite"), primary_key=True)
    name = db.Column(db.String(150), unique=True, nullable=False)
    short_name = db.Column(db.String(20))
    city = db.Column(db.String(100))
    coach = db.Column(db.String(150))
    founded = db.Column(db.String(4))
    logo_path = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=utcnow)
    created_by = db.Column(db.BigInteger, db.ForeignKey('users.id'), nullable=True)

    # convenience: fixtures where this team is home/away
    home_fixtures = db.relationship(
        "Fixture",
        foreign_keys="Fixture.home_team_id",
        back_populates="home_team",
        lazy="dynamic",
        passive_deletes=True
    )
    away_fixtures = db.relationship(
        "Fixture",
        foreign_keys="Fixture.away_team_id",
        back_populates="away_team",
        lazy="dynamic",
        passive_deletes=True
    )

    # many-to-many: players assigned to this team via team_players.
    # Read-only convenience view: memberships are written through the
    # TeamPlayer association model, so this side must not also write to
    # team_players (avoids SQLAlchemy's "relationship overlaps" conflict).
    players = db.relationship(
        "Player",
        secondary="team_players",
        backref=db.backref("teams", lazy="dynamic", viewonly=True),
        lazy="dynamic",
        viewonly=True
    )

    def __repr__(self):
        return f"<Team {self.name}>"

class Player(db.Model):
    __tablename__ = 'players'

    id = db.Column(db.BigInteger().with_variant(db.Integer, "sqlite"), primary_key=True)
    first_name = db.Column(db.String(80), nullable=False)
    last_name = db.Column(db.String(80))
    dob = db.Column(db.Date)
    nationality = db.Column(db.String(80))
    height_cm = db.Column(db.SmallInteger)
    weight_kg = db.Column(db.SmallInteger)
    position = db.Column(db.String(50))
    preferred_foot = db.Column(
        db.Enum('left', 'right', 'both', name='foot'),
        default='right'
    )
    created_at = db.Column(db.DateTime, default=utcnow)

    def __repr__(self):
        return f"<Player {self.first_name} {self.last_name}>"

class TeamPlayer(db.Model):
    __tablename__ = 'team_players'

    id = db.Column(db.BigInteger().with_variant(db.Integer, "sqlite"), primary_key=True)
    team_id = db.Column(
        db.BigInteger,
        db.ForeignKey('teams.id', ondelete='CASCADE'),
        nullable=False
    )
    player_id = db.Column(
        db.BigInteger,
        db.ForeignKey('players.id', ondelete='CASCADE'),
        nullable=False
    )
    squad_number = db.Column(db.SmallInteger)
    joined_at = db.Column(db.Date)
    left_at = db.Column(db.Date)
    role = db.Column(db.String(50), default='player')
    created_at = db.Column(db.DateTime, default=utcnow)

    team = db.relationship("Team", backref=db.backref(
        "team_players",
        cascade="all, delete-orphan",
        passive_deletes=True
    ))
    player = db.relationship("Player", backref=db.backref(
        "team_players",
        cascade="all, delete-orphan",
        passive_deletes=True
    ))

    def __repr__(self):
        return f"<TeamPlayer team={self.team_id} player={self.player_id}>"

class Venue(db.Model):
    __tablename__ = 'venues'

    id = db.Column(db.BigInteger().with_variant(db.Integer, "sqlite"), primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    address = db.Column(db.String(255))
    city = db.Column(db.String(100))
    capacity = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=utcnow)

    def __repr__(self):
        return f"<Venue {self.name}>"

class Fixture(db.Model):
    __tablename__ = 'fixtures'

    id = db.Column(db.BigInteger().with_variant(db.Integer, "sqlite"), primary_key=True)

    event_id = db.Column(
        db.BigInteger,
        db.ForeignKey('events.id', ondelete='CASCADE'),
        nullable=True
    )

    stage = db.Column(db.String(100))
    matchday = db.Column(db.Integer, default=1)

    home_team_id = db.Column(
        db.BigInteger,
        db.ForeignKey('teams.id', ondelete='CASCADE'),
        nullable=False
    )
    away_team_id = db.Column(
        db.BigInteger,
        db.ForeignKey('teams.id', ondelete='CASCADE'),
        nullable=False
    )

    venue_id = db.Column(
        db.BigInteger,
        db.ForeignKey('venues.id'),
        nullable=True
    )

    scheduled_at = db.Column(db.DateTime, nullable=True)
    status = db.Column(
        db.Enum('scheduled', 'postponed', 'cancelled', 'completed', name='fixture_status'),
        default='scheduled'
    )
    created_by = db.Column(db.BigInteger, db.ForeignKey('users.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=utcnow)

    # relationships
    home_team = db.relationship(
        "Team",
        foreign_keys=[home_team_id],
        back_populates="home_fixtures",
        passive_deletes=True
    )
    away_team = db.relationship(
        "Team",
        foreign_keys=[away_team_id],
        back_populates="away_fixtures",
        passive_deletes=True
    )
    event = db.relationship("Event", back_populates="fixtures")
    venue = db.relationship("Venue")

    def __repr__(self):
        return f"<Fixture {self.id}>"

class Match(db.Model):
    __tablename__ = 'matches'

    id = db.Column(db.BigInteger().with_variant(db.Integer, "sqlite"), primary_key=True)
    fixture_id = db.Column(
        db.BigInteger,
        db.ForeignKey('fixtures.id', ondelete='CASCADE'),
        unique=True,
        nullable=False
    )
    home_score = db.Column(db.SmallInteger, default=0)
    away_score = db.Column(db.SmallInteger, default=0)
    winner_team_id = db.Column(db.BigInteger, db.ForeignKey('teams.id'))
    played_at = db.Column(db.DateTime)
    status = db.Column(
        db.Enum('scheduled', 'in_progress', 'completed', name='match_status'),
        default='scheduled'
    )
    created_at = db.Column(db.DateTime, default=utcnow)

    fixture = db.relationship("Fixture")
    winner_team = db.relationship("Team")

    def __repr__(self):
        return f"<Match {self.id}>"

class PlayerStat(db.Model):
    __tablename__ = 'player_stats'

    id = db.Column(db.BigInteger().with_variant(db.Integer, "sqlite"), primary_key=True)
    match_id = db.Column(
        db.BigInteger,
        db.ForeignKey('matches.id', ondelete='CASCADE'),
        nullable=False
    )
    player_id = db.Column(db.BigInteger, db.ForeignKey('players.id'), nullable=False)
    team_id = db.Column(db.BigInteger, db.ForeignKey('teams.id'), nullable=False)

    goals = db.Column(db.SmallInteger, default=0)
    assists = db.Column(db.SmallInteger, default=0)
    yellow_cards = db.Column(db.SmallInteger, default=0)
    red_cards = db.Column(db.SmallInteger, default=0)
    minutes_played = db.Column(db.SmallInteger, default=0)

    meta = db.Column(db.JSON, nullable=True)
    created_at = db.Column(db.DateTime, default=utcnow)

    match = db.relationship("Match")
    player = db.relationship("Player")
    team = db.relationship("Team")

    def __repr__(self):
        return f"<PlayerStat match={self.match_id} player={self.player_id}>"
