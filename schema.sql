CREATE TABLE `admin` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `username` VARCHAR(255) NOT NULL UNIQUE,
    `password` VARCHAR(255) NOT NULL
);

CREATE TABLE `user` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `name` VARCHAR(255) NOT NULL,
    `username` VARCHAR(255) NOT NULL UNIQUE,
    `password` VARCHAR(255) NOT NULL,
    `dob` DATE,
    `blocked` BOOLEAN DEFAULT FALSE
);

CREATE TABLE `subject` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `name` VARCHAR(255) NOT NULL,
    `description` VARCHAR(255)
);

CREATE TABLE `chapter` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `subject_id` INT NOT NULL,
    `name` VARCHAR(255) NOT NULL,
    `description` VARCHAR(255),
    FOREIGN KEY (`subject_id`) REFERENCES `subject` (`id`)
);

CREATE TABLE `question` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `chapter_id` INT NOT NULL,
    `title` VARCHAR(255) NOT NULL,
    `statement` VARCHAR(255) NOT NULL UNIQUE,
    `option1` VARCHAR(31) NOT NULL,
    `option2` VARCHAR(31) NOT NULL,
    `option3` VARCHAR(31) NOT NULL,
    `option4` VARCHAR(31) NOT NULL,
    `correct_option` INT NOT NULL,
    FOREIGN KEY (`chapter_id`) REFERENCES `chapter` (`id`)
);

CREATE TABLE `quiz` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `subject_id` INT NOT NULL,
    `name` VARCHAR(255) NOT NULL,
    `quiz_date` DATE NOT NULL,
    `time_duration` TIME NOT NULL,
    FOREIGN KEY (`subject_id`) REFERENCES `subject` (`id`)
);

CREATE TABLE `quizwisequestion` (
    `quiz_id` INT NOT NULL,
    `question_id` INT NOT NULL,
    PRIMARY KEY (`quiz_id`, `question_id`),
    FOREIGN KEY (`quiz_id`) REFERENCES `quiz` (`id`),
    FOREIGN KEY (`question_id`) REFERENCES `question` (`id`)
);

CREATE TABLE `score` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `user_id` INT NOT NULL,
    `quiz_name` VARCHAR(255) NOT NULL,
    `quiz_date` DATE NOT NULL,
    `quiz_time_duration` TIME NOT NULL,
    `subject_name` VARCHAR(255) NOT NULL,
    `no_of_questions` INT NOT NULL,
    `start_time` DATETIME,
    `end_time` DATETIME,
    `user_score` INT NOT NULL,
    FOREIGN KEY (`user_id`) REFERENCES `user` (`id`)
);