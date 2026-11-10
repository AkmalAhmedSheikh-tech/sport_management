-- 1) Create database
CREATE DATABASE IF NOT EXISTS sports_league_manager
  CHARACTER SET = utf8mb4
  COLLATE = utf8mb4_unicode_ci;
USE sports_league_manager;

-- 2) Users table (auth)
CREATE TABLE users (
  id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  username VARCHAR(80) NOT NULL UNIQUE,
  email VARCHAR(255) NOT NULL UNIQUE,
  password_hash VARCHAR(255) NOT NULL, -- store bcrypt/werkzeug hash created by app layer
  role ENUM('admin','manager','viewer') NOT NULL DEFAULT 'manager',
  is_active TINYINT(1) NOT NULL DEFAULT 1,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  last_login TIMESTAMP NULL
) ENGINE=InnoDB;

-- 3) Events (tournaments / templates)
CREATE TABLE events (
  id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(150) NOT NULL,
  slug VARCHAR(150) NOT NULL,
  description TEXT,
  sport_type VARCHAR(50) DEFAULT 'football',
  season VARCHAR(50),
  is_template TINYINT(1) NOT NULL DEFAULT 0,
  start_date DATE,
  end_date DATE,
  created_by BIGINT UNSIGNED,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  UNIQUE KEY ux_event_slug (slug),
  FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE SET NULL
) ENGINE=InnoDB;

-- 4) Teams
CREATE TABLE teams (
  id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(150) NOT NULL,
  short_name VARCHAR(20),
  city VARCHAR(100),
  coach VARCHAR(150),
  founded YEAR,
  logo_path VARCHAR(255),
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  created_by BIGINT UNSIGNED,
  UNIQUE KEY ux_team_name (name),
  FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE SET NULL
) ENGINE=InnoDB;

-- 5) Players
CREATE TABLE players (
  id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  first_name VARCHAR(80) NOT NULL,
  last_name VARCHAR(80),
  dob DATE,
  nationality VARCHAR(80),
  height_cm SMALLINT,
  weight_kg SMALLINT,
  position VARCHAR(50),
  preferred_foot ENUM('left','right','both') DEFAULT 'right',
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- 6) Team roster (player membership)
CREATE TABLE team_players (
  id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  team_id BIGINT UNSIGNED NOT NULL,
  player_id BIGINT UNSIGNED NOT NULL,
  squad_number SMALLINT,
  joined_at DATE,
  left_at DATE,
  role VARCHAR(50) DEFAULT 'player',
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  UNIQUE KEY ux_team_player (team_id, player_id),
  FOREIGN KEY (team_id) REFERENCES teams(id) ON DELETE CASCADE,
  FOREIGN KEY (player_id) REFERENCES players(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- 7) Venues (stadiums)
CREATE TABLE venues (
  id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(150) NOT NULL,
  address VARCHAR(255),
  city VARCHAR(100),
  capacity INT,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- 8) Fixtures (scheduled matches)
CREATE TABLE fixtures (
  id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  event_id BIGINT UNSIGNED NULL, -- optional: the app allows fixtures without an event
  stage VARCHAR(100),
  matchday INT DEFAULT 1,
  home_team_id BIGINT UNSIGNED NOT NULL,
  away_team_id BIGINT UNSIGNED NOT NULL,
  venue_id BIGINT UNSIGNED,
  scheduled_at DATETIME,
  status ENUM('scheduled','postponed','cancelled','completed') DEFAULT 'scheduled',
  created_by BIGINT UNSIGNED,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (event_id) REFERENCES events(id) ON DELETE CASCADE,
  FOREIGN KEY (home_team_id) REFERENCES teams(id),
  FOREIGN KEY (away_team_id) REFERENCES teams(id),
  FOREIGN KEY (venue_id) REFERENCES venues(id),
  FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE SET NULL
) ENGINE=InnoDB;

-- 9) Matches (actual results; one match record per played fixture)
CREATE TABLE matches (
  id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  fixture_id BIGINT UNSIGNED NOT NULL UNIQUE,
  home_score SMALLINT DEFAULT 0,
  away_score SMALLINT DEFAULT 0,
  winner_team_id BIGINT UNSIGNED NULL, -- NULL for draw
  played_at DATETIME,
  status ENUM('scheduled','in_progress','completed') DEFAULT 'scheduled',
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (fixture_id) REFERENCES fixtures(id) ON DELETE CASCADE,
  FOREIGN KEY (winner_team_id) REFERENCES teams(id)
) ENGINE=InnoDB;

-- 10) Player statistics per match
CREATE TABLE player_stats (
  id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  match_id BIGINT UNSIGNED NOT NULL,
  player_id BIGINT UNSIGNED NOT NULL,
  team_id BIGINT UNSIGNED NOT NULL,
  goals SMALLINT DEFAULT 0,
  assists SMALLINT DEFAULT 0,
  yellow_cards SMALLINT DEFAULT 0,
  red_cards SMALLINT DEFAULT 0,
  minutes_played SMALLINT DEFAULT 0,
  meta JSON DEFAULT NULL,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (match_id) REFERENCES matches(id) ON DELETE CASCADE,
  FOREIGN KEY (player_id) REFERENCES players(id),
  FOREIGN KEY (team_id) REFERENCES teams(id),
  UNIQUE KEY ux_player_match (match_id, player_id)
) ENGINE=InnoDB;

-- 11) Optional table to store league standings summary for speed (can be computed)
CREATE TABLE team_stats (
  id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  event_id BIGINT UNSIGNED NOT NULL,
  team_id BIGINT UNSIGNED NOT NULL,
  played INT DEFAULT 0,
  wins INT DEFAULT 0,
  draws INT DEFAULT 0,
  losses INT DEFAULT 0,
  goals_for INT DEFAULT 0,
  goals_against INT DEFAULT 0,
  goal_diff INT AS (goals_for - goals_against) STORED,
  points INT DEFAULT 0,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  UNIQUE KEY ux_event_team (event_id, team_id),
  FOREIGN KEY (event_id) REFERENCES events(id) ON DELETE CASCADE,
  FOREIGN KEY (team_id) REFERENCES teams(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- 12) Audit table
CREATE TABLE audits (
  id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  user_id BIGINT UNSIGNED,
  action VARCHAR(100) NOT NULL,
  details JSON,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
) ENGINE=InnoDB;

-- 13) Example indexes for common queries
CREATE INDEX idx_fixtures_event_matchday ON fixtures (event_id, matchday);
CREATE INDEX idx_matches_played_at ON matches (played_at);
CREATE INDEX idx_player_stats_player ON player_stats (player_id);

