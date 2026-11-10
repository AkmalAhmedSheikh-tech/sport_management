from flask import Flask, render_template, redirect, url_for, flash, request
from config import Config
from models import db, User, Team, Player, Fixture, Event, Match, TeamPlayer, PlayerStat
from sqlalchemy import or_
from utils import hash_password, verify_password, slugify, utcnow, parse_date
from datetime import datetime

from flask_login import (
    LoginManager,
    login_user,
    login_required,
    logout_user,
    current_user,
    UserMixin
)

class LoginUser(UserMixin):
    def __init__(self, user):
        self.id = user.id
        self.username = user.username
        self.user = user

    def get_id(self):
        return str(self.id)

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)

    login_manager = LoginManager()
    login_manager.login_view = 'login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        user = db.session.get(User, int(user_id))
        if user:
            return LoginUser(user)
        return None

    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/register', methods=['GET', 'POST'])
    def register():
        if request.method == 'POST':
            username = request.form.get('username')
            email = request.form.get('email')
            password = request.form.get('password')

            existing = User.query.filter(
                (User.username == username) | (User.email == email)
            ).first()
            if existing:
                flash('Username or email already exists.', 'warning')
                return redirect(url_for('register'))

            pw_hash = hash_password(password)
            user = User(username=username, email=email, password_hash=pw_hash)
            db.session.add(user)
            db.session.commit()

            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('login'))

        return render_template('register.html')

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            username = request.form.get('username')
            password = request.form.get('password')
            user = User.query.filter_by(username=username).first()

            if user and verify_password(user.password_hash, password):
                login_user(LoginUser(user))
                user.last_login = db.func.now()
                db.session.commit()
                return redirect(url_for('dashboard'))

            flash('Invalid username or password.', 'danger')
            return redirect(url_for('login'))

        return render_template('login.html')

    @app.route('/logout')
    @login_required
    def logout():
        logout_user()
        flash('Logged out successfully.', 'info')
        return redirect(url_for('index'))

    @app.route('/dashboard')
    @login_required
    def dashboard():
        teams = Team.query.order_by(Team.name).limit(10).all()
        players = Player.query.limit(9).all()
        now = utcnow()

        upcoming_fixtures = (
            Fixture.query
            .filter(Fixture.scheduled_at != None)
            .filter(Fixture.scheduled_at >= now)
            .order_by(Fixture.scheduled_at.asc())
            .limit(5)
            .all()
        )

        events = (
            Event.query
            .order_by(Event.start_date.desc())
            .limit(5)
            .all()
        )

        return render_template(
            'dashboard.html',
            teams=teams,
            players=players,
            upcoming_fixtures=upcoming_fixtures,
            events=events
        )

    @app.route('/teams')
    @login_required
    def teams_view():
        teams = Team.query.all()
        return render_template('teams.html', teams=teams)

    @app.route('/teams/add', methods=['GET', 'POST'])
    @login_required
    def add_team():
        if request.method == 'POST':
            name = (request.form.get('name') or '').strip()
            short_name = request.form.get('short_name')
            city = request.form.get('city')
            coach = request.form.get('coach')
            player_ids = request.form.getlist('player_ids')

            if not name:
                flash('Team name is required.', 'warning')
                return redirect(url_for('add_team'))

            if Team.query.filter_by(name=name).first():
                flash(f'A team named "{name}" already exists.', 'warning')
                return redirect(url_for('add_team'))

            team = Team(
                name=name,
                short_name=short_name,
                city=city,
                coach=coach,
                created_by=current_user.id
            )

            db.session.add(team)
            db.session.flush()

            for pid in player_ids:
                try:
                    pid_int = int(pid)
                    link = TeamPlayer(team_id=team.id, player_id=pid_int)
                    db.session.add(link)
                except ValueError:
                    continue

            db.session.commit()
            flash('Team added successfully!', 'success')
            return redirect(url_for('teams_view'))

        players = Player.query.order_by(Player.first_name, Player.last_name).all()
        return render_template('add_team.html', players=players)

    @app.route('/teams/edit/<int:team_id>', methods=['GET', 'POST'])
    @login_required
    def edit_team(team_id):
        team = db.get_or_404(Team, team_id)

        if request.method == 'POST':
            new_name = (request.form.get('name') or '').strip()

            if not new_name:
                flash('Team name is required.', 'warning')
                return redirect(url_for('edit_team', team_id=team.id))

            if Team.query.filter(Team.name == new_name, Team.id != team.id).first():
                flash(f'A team named "{new_name}" already exists.', 'warning')
                return redirect(url_for('edit_team', team_id=team.id))

            team.name = new_name
            team.short_name = request.form.get('short_name')
            team.city = request.form.get('city')
            team.coach = request.form.get('coach')
            player_ids = request.form.getlist('player_ids')

            TeamPlayer.query.filter_by(team_id=team.id).delete()

            for pid in player_ids:
                try:
                    pid_int = int(pid)
                    db.session.add(TeamPlayer(team_id=team.id, player_id=pid_int))
                except ValueError:
                    continue

            db.session.commit()
            flash('Team updated successfully!', 'success')
            return redirect(url_for('teams_view'))

        players = Player.query.order_by(Player.first_name, Player.last_name).all()
        current_player_ids = {
            tp.player_id for tp in TeamPlayer.query.filter_by(team_id=team.id).all()
        }

        return render_template(
            'edit_team.html',
            team=team,
            players=players,
            current_player_ids=current_player_ids
        )

    @app.route('/teams/<int:team_id>')
    @login_required
    def team_detail(team_id):
        team = db.get_or_404(Team, team_id)
        return render_template('team_detail.html', team=team)

    @app.route('/teams/delete/<int:team_id>', methods=['POST'])
    @login_required
    def delete_team(team_id):
        team = db.get_or_404(Team, team_id)

        try:
            current_user_id = int(current_user.get_id())
            created_by = team.created_by
            is_owner = (created_by is not None and current_user_id == int(created_by))
        except Exception:
            is_owner = False

        is_admin = False
        try:
            # users.role is an ENUM('admin','manager','viewer'); there is no is_admin column
            is_admin = getattr(current_user.user, 'role', None) == 'admin'
        except Exception:
            is_admin = False

        if not (is_owner or is_admin):
            flash('You are not authorized to delete this team.', 'danger')
            return redirect(url_for('teams_view'))

        Fixture.query.filter(
            or_(
                Fixture.home_team_id == team.id,
                Fixture.away_team_id == team.id
            )
        ).delete(synchronize_session=False)

        TeamPlayer.query.filter_by(team_id=team.id).delete(synchronize_session=False)
        PlayerStat.query.filter_by(team_id=team.id).delete(synchronize_session=False)

        db.session.delete(team)
        db.session.commit()

        flash(f'Team "{team.name}" and its related fixtures were deleted.', 'info')
        return redirect(url_for('teams_view'))

    @app.route('/players')
    @login_required
    def players_view():
        players = Player.query.all()
        return render_template('players.html', players=players)

    @app.route('/players/add', methods=['GET', 'POST'])
    @login_required
    def add_player():
        if request.method == 'POST':
            first = request.form.get('first_name')
            last = request.form.get('last_name')
            position = request.form.get('position')

            player = Player(first_name=first, last_name=last, position=position)

            db.session.add(player)
            db.session.commit()

            flash('Player added successfully!', 'success')
            return redirect(url_for('players_view'))

        return render_template('add_player.html')

    @app.route('/players/delete/<int:player_id>', methods=['POST'])
    @login_required
    def delete_player(player_id):
        player = db.get_or_404(Player, player_id)
        TeamPlayer.query.filter_by(player_id=player.id).delete(synchronize_session=False)
        PlayerStat.query.filter_by(player_id=player.id).delete(synchronize_session=False)
        db.session.delete(player)
        db.session.commit()

        flash(f'Player "{player.first_name} {player.last_name}" deleted.', 'info')
        return redirect(url_for('players_view'))

    @app.route('/fixtures')
    @login_required
    def fixtures_view():
        fixtures = Fixture.query.all()
        return render_template('fixtures.html', fixtures=fixtures)

    @app.route('/fixtures/add', methods=['GET', 'POST'])
    @login_required
    def add_fixture():
        if request.method == 'POST':
            event_id_raw = request.form.get('event_id', '').strip()

            if event_id_raw:
                try:
                    event_id = int(event_id_raw)
                except ValueError:
                    flash("Invalid event selected.", "warning")
                    return redirect(url_for('add_fixture'))

                event = db.session.get(Event, event_id)
                if not event:
                    flash("Selected event does not exist.", "danger")
                    return redirect(url_for('add_event'))
            else:
                event_id = None

            home_id = request.form.get('home_team_id')
            away_id = request.form.get('away_team_id')

            if not home_id or not away_id:
                flash("Both home and away team are required.", "warning")
                return redirect(url_for('add_fixture'))

            if home_id == away_id:
                flash("Home and away team must be different.", "warning")
                return redirect(url_for('add_fixture'))

            scheduled_raw = request.form.get('scheduled_at', '').strip()
            scheduled_at = None
            if scheduled_raw:
                try:
                    scheduled_at = datetime.strptime(scheduled_raw, "%Y-%m-%dT%H:%M")
                except ValueError:
                    flash("Invalid date/time format.", "warning")
                    return redirect(url_for('add_fixture'))

            fixture = Fixture(
                event_id=event_id,
                home_team_id=home_id,
                away_team_id=away_id,
                scheduled_at=scheduled_at,
                status='scheduled',
                created_by=current_user.id
            )

            db.session.add(fixture)
            db.session.commit()

            flash('Fixture successfully scheduled!', 'success')
            return redirect(url_for('fixtures_view'))

        teams = Team.query.all()
        events = Event.query.all()
        selected_event_id = request.args.get('event_id', type=int)

        return render_template(
            'add_fixture.html',
            teams=teams,
            events=events,
            selected_event_id=selected_event_id
        )

    @app.route('/fixtures/delete/<int:fixture_id>', methods=['POST'])
    @login_required
    def delete_fixture(fixture_id):
        fixture = db.get_or_404(Fixture, fixture_id)
        db.session.delete(fixture)
        db.session.commit()
        flash('Fixture deleted.', 'info')
        return redirect(url_for('fixtures_view'))

    @app.route('/events')
    @login_required
    def events_view():
        events = Event.query.order_by(Event.start_date.desc()).all()
        return render_template('events.html', events=events)

    @app.route('/events/add', methods=['GET', 'POST'])
    @login_required
    def add_event():
        if request.method == 'POST':
            name = request.form.get('name', '').strip()
            description = request.form.get('description', '').strip()
            sport_type = request.form.get('sport_type', 'football').strip()
            season = request.form.get('season', '').strip()
            if not name:
                flash('Event name is required.', 'warning')
                return redirect(url_for('add_event'))

            try:
                start_date = parse_date(request.form.get('start_date'))
                end_date = parse_date(request.form.get('end_date'))
            except ValueError:
                flash('Invalid date. Use the YYYY-MM-DD format.', 'warning')
                return redirect(url_for('add_event'))

            base_slug = slugify(name)
            slug = base_slug
            i = 1
            while Event.query.filter_by(slug=slug).first():
                slug = f"{base_slug}-{i}"
                i += 1

            ev = Event(
                name=name,
                slug=slug,
                description=description,
                sport_type=sport_type,
                season=season,
                start_date=start_date or None,
                end_date=end_date or None,
                created_by=current_user.id
            )
            db.session.add(ev)
            db.session.commit()
            flash('Event created successfully!', 'success')
            return redirect(url_for('events_view'))

        return render_template('add_event.html')

    @app.route('/events/edit/<int:event_id>', methods=['GET', 'POST'])
    @login_required
    def edit_event(event_id):
        ev = db.get_or_404(Event, event_id)

        if request.method == 'POST':
            name = request.form.get('name', '').strip()
            description = request.form.get('description', '').strip()
            sport_type = request.form.get('sport_type', 'football').strip()
            season = request.form.get('season', '').strip()

            if not name:
                flash('Event name is required.', 'warning')
                return redirect(url_for('edit_event', event_id=event_id))

            try:
                start_date = parse_date(request.form.get('start_date'))
                end_date = parse_date(request.form.get('end_date'))
            except ValueError:
                flash('Invalid date. Use the YYYY-MM-DD format.', 'warning')
                return redirect(url_for('edit_event', event_id=event_id))

            ev.name = name
            ev.description = description
            ev.sport_type = sport_type
            ev.season = season
            ev.start_date = start_date or None
            ev.end_date = end_date or None

            new_slug = slugify(name)
            if new_slug != ev.slug:
                base_slug = new_slug
                slug = base_slug
                i = 1
                while Event.query.filter(Event.slug == slug, Event.id != ev.id).first():
                    slug = f"{base_slug}-{i}"
                    i += 1
                ev.slug = slug

            db.session.commit()
            flash('Event updated.', 'success')
            return redirect(url_for('events_view'))

        return render_template('edit_event.html', event=ev)

    @app.route('/events/delete/<int:event_id>', methods=['POST'])
    @login_required
    def delete_event(event_id):
        ev = db.get_or_404(Event, event_id)
        db.session.delete(ev)
        db.session.commit()
        flash('Event deleted.', 'info')
        return redirect(url_for('events_view'))

    @app.route('/events/<int:event_id>')
    @login_required
    def event_detail(event_id):
        ev = db.get_or_404(Event, event_id)
        fixtures = Fixture.query.filter_by(event_id=event_id) \
                                .order_by(Fixture.scheduled_at.desc()) \
                                .all()
        return render_template('event_detail.html', event=ev, fixtures=fixtures)

    return app

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        db.create_all()
    app.run(debug=True)
