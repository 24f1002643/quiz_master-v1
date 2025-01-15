CREATE TABLE admin (
    id INT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL
);

CREATE TABLE user (
    id INT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255) NOT NULL,
    username VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    dob DATE,
    blocked BOOLEAN DEFAULT 0
);

CREATE TABLE subject (
    id INT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255) NOT NULL,
    description VARCHAR(255)
);

CREATE TABLE chapter (
    id INT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
    subject_id INT UNSIGNED NOT NULL,
    name VARCHAR(255) NOT NULL,
    description VARCHAR(255),
    FOREIGN KEY (subject_id) REFERENCES subject(id)
);

CREATE TABLE quiz (
    id INT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
    subject_id INT UNSIGNED NOT NULL,
    name VARCHAR(255) NOT NULL,
    quiz_date DATE NOT NULL,
    time_duration TIME NOT NULL,
    FOREIGN KEY (subject_id) REFERENCES subject(id)
);

CREATE TABLE question (
    id INT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
    chapter_id INT UNSIGNED NOT NULL,
    title VARCHAR(255) NOT NULL,
    statement VARCHAR(255) NOT NULL UNIQUE,
    option1 VARCHAR(31) NOT NULL,
    option2 VARCHAR(31) NOT NULL,
    option3 VARCHAR(31) NOT NULL,
    option4 VARCHAR(31) NOT NULL,
    correct_option INT NOT NULL,
    FOREIGN KEY (chapter_id) REFERENCES chapter(id)
);

CREATE TABLE quizwisequestion (
    quiz_id INT UNSIGNED NOT NULL,
    question_id INT UNSIGNED NOT NULL,
    PRIMARY KEY (quiz_id, question_id),
    FOREIGN KEY (quiz_id) REFERENCES quiz(id),
    FOREIGN KEY (question_id) REFERENCES question(id)
);

CREATE TABLE score (
    id INT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
    quiz_id INT UNSIGNED NOT NULL,
    user_id INT UNSIGNED NOT NULL,
    start_time DATETIME,
    end_time DATETIME,
    user_score INT NOT NULL,
    FOREIGN KEY (quiz_id) REFERENCES quiz(id),
    FOREIGN KEY (user_id) REFERENCES user(id)
);