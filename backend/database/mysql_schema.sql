CREATE DATABASE IF NOT EXISTS portfolio_weirdos CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE portfolio_weirdos;

DROP TABLE IF EXISTS canvas_layouts;
DROP TABLE IF EXISTS usability_feedback;
DROP TABLE IF EXISTS reflections;
DROP TABLE IF EXISTS habits;
DROP TABLE IF EXISTS identity_traits;
DROP TABLE IF EXISTS achievements;
DROP TABLE IF EXISTS skills;
DROP TABLE IF EXISTS experiences;
DROP TABLE IF EXISTS education;
DROP TABLE IF EXISTS profiles;
DROP TABLE IF EXISTS users;

CREATE TABLE users (
  id INT AUTO_INCREMENT PRIMARY KEY,
  full_name VARCHAR(120) NOT NULL,
  email VARCHAR(160) NOT NULL UNIQUE,
  password_hash VARCHAR(255) NOT NULL,
  role VARCHAR(40) NOT NULL DEFAULT 'student',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE profiles (
  id INT AUTO_INCREMENT PRIMARY KEY,
  user_id INT NOT NULL,
  display_name VARCHAR(120) NOT NULL,
  headline VARCHAR(180) NOT NULL,
  location VARCHAR(120),
  bio TEXT,
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE education (
  id INT AUTO_INCREMENT PRIMARY KEY,
  user_id INT NOT NULL,
  institution VARCHAR(160) NOT NULL,
  qualification VARCHAR(180) NOT NULL,
  start_year INT,
  end_year INT,
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE experiences (
  id INT AUTO_INCREMENT PRIMARY KEY,
  user_id INT NOT NULL,
  title VARCHAR(160) NOT NULL,
  organization VARCHAR(160) NOT NULL,
  description TEXT,
  start_date DATE,
  end_date DATE,
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE skills (
  id INT AUTO_INCREMENT PRIMARY KEY,
  user_id INT NOT NULL,
  name VARCHAR(120) NOT NULL,
  category VARCHAR(80) NOT NULL,
  confidence_level TINYINT NOT NULL CHECK (confidence_level BETWEEN 1 AND 5),
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE achievements (
  id INT AUTO_INCREMENT PRIMARY KEY,
  user_id INT NOT NULL,
  title VARCHAR(180) NOT NULL,
  description TEXT,
  achieved_on DATE,
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE identity_traits (
  id INT AUTO_INCREMENT PRIMARY KEY,
  user_id INT NOT NULL,
  trait_name VARCHAR(120) NOT NULL,
  trait_type VARCHAR(60) NOT NULL,
  description TEXT,
  visibility VARCHAR(40) NOT NULL DEFAULT 'public',
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE habits (
  id INT AUTO_INCREMENT PRIMARY KEY,
  user_id INT NOT NULL,
  name VARCHAR(140) NOT NULL,
  frequency VARCHAR(80),
  identity_link TEXT,
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE reflections (
  id INT AUTO_INCREMENT PRIMARY KEY,
  user_id INT NOT NULL,
  title VARCHAR(180) NOT NULL,
  body TEXT NOT NULL,
  mood VARCHAR(80),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE usability_feedback (
  id INT AUTO_INCREMENT PRIMARY KEY,
  visitor_name VARCHAR(120) DEFAULT 'Anonymous',
  clarity_rating TINYINT NOT NULL CHECK (clarity_rating BETWEEN 1 AND 5),
  identity_rating TINYINT NOT NULL CHECK (identity_rating BETWEEN 1 AND 5),
  comments TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE canvas_layouts (
  id INT AUTO_INCREMENT PRIMARY KEY,
  user_id INT NOT NULL UNIQUE,
  canvas_width INT NOT NULL DEFAULT 1000,
  canvas_height INT NOT NULL DEFAULT 1300,
  background_color VARCHAR(20) NOT NULL DEFAULT '#ffffff',
  elements LONGTEXT NOT NULL,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

INSERT INTO users (id, full_name, email, password_hash, role) VALUES
(1, 'Sujit Khadgi', 'sujit@example.com', 'pbkdf2_sha256$706f7274666f6c696f5f666f725f77656972646f735f73656564$4db137a9bb3348fbb99b899a5f04bba2ef379757c8c817076d903ff45dd2c6a8', 'student');

INSERT INTO profiles (user_id, display_name, headline, location, bio) VALUES
(1, 'Sujit Khadgi', 'Computing student building a relational portfolio for full-person identity', 'Birmingham / Kathmandu', 'A portfolio that includes the formal evidence of skill and the more human details: habits, contradictions, creative energy, strengths, weaknesses, and reflections.');

INSERT INTO education (user_id, institution, qualification, start_year, end_year) VALUES
(1, 'Birmingham City University', 'CMP6200 Individual Honours Project', 2025, 2026),
(1, 'School of Computing and Digital Technology', 'Undergraduate Computing pathway', 2024, 2026);

INSERT INTO experiences (user_id, title, organization, description, start_date, end_date) VALUES
(1, 'Project Developer', 'Portfolio for Weirdos', 'Designed a prototype portfolio system that combines professional records with structured identity attributes.', '2025-12-01', NULL);

INSERT INTO skills (user_id, name, category, confidence_level) VALUES
(1, 'Relational database design', 'Technical', 4),
(1, 'Human-centred design', 'Design', 4),
(1, 'Prototype development', 'Technical', 4),
(1, 'Reflective writing', 'Identity', 5);

INSERT INTO achievements (user_id, title, description, achieved_on) VALUES
(1, 'Project interim report completed', 'Defined the problem, aims, objectives, scope, methodology, risks, and ethics for Portfolio for Weirdos.', '2026-03-06');

INSERT INTO identity_traits (user_id, trait_name, trait_type, description, visibility) VALUES
(1, 'Creative outsider thinking', 'strength', 'Looks for unusual angles instead of only repeating standard portfolio formats.', 'public'),
(1, 'Overthinking useful details', 'weakness', 'Can spend too long polishing ideas, but it often reveals better design questions.', 'public'),
(1, 'Playful seriousness', 'personality', 'Takes meaningful work seriously without making the whole experience lifeless.', 'public');

INSERT INTO habits (user_id, name, frequency, identity_link) VALUES
(1, 'Collecting odd project ideas', 'Weekly', 'Keeps the portfolio connected to curiosity and non-traditional learning.'),
(1, 'Writing reflection notes', 'After milestones', 'Turns personal development into structured evidence.');

INSERT INTO reflections (user_id, title, body, mood) VALUES
(1, 'Why this portfolio exists', 'Traditional portfolios show achievement, but they often miss the person behind the achievement. This prototype stores both.', 'Focused');

INSERT INTO usability_feedback (visitor_name, clarity_rating, identity_rating, comments) VALUES
('Sample tester', 5, 5, 'The portfolio makes the identity traits visible without losing structure.');


