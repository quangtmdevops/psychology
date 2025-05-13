-- Xóa bảng nếu tồn tại (để đảm bảo clean slate khi chạy lại)
DROP TABLE IF EXISTS test_answer, Entity, test, situational_question, sub_group, group, post, user;

-- Bảng user
CREATE TABLE user (
    id INT PRIMARY KEY,
    email VARCHAR(255) NOT NULL,
    reward INT DEFAULT 0,
    isPremium BOOLEAN DEFAULT FALSE
);

-- Bảng group (chủ đề lớn)
CREATE TABLE group (
    id INT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT
);

-- Bảng sub_group (chủ đề con)
CREATE TABLE sub_group (
    id INT PRIMARY KEY,
    groupId INT NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    FOREIGN KEY (groupId) REFERENCES group(id)
);

-- Bảng situational_question
CREATE TABLE situational_question (
    id INT PRIMARY KEY,
    groupId INT NOT NULL,
    content TEXT NOT NULL,
    level INT CHECK (level IN (1, 2, 3)),
    FOREIGN KEY (groupId) REFERENCES group(id)
);

-- Bảng post
CREATE TABLE post (
    id INT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    content TEXT,
    audio TEXT,
    image TEXT,
    createAt TIMESTAMP
);

-- Bảng test
CREATE TABLE test (
    id INT PRIMARY KEY,
    content TEXT NOT NULL,
    `order` INT
);

-- Bảng test_answer
CREATE TABLE test_answer (
    id INT PRIMARY KEY,
    questionId INT NOT NULL,
    level INT CHECK (level >= 1 AND level <= 3),
    FOREIGN KEY (questionId) REFERENCES test(id)
);

-- Bảng Entity
CREATE TABLE Entity (
    id INT PRIMARY KEY,
    questionId INT NOT NULL,
    content TEXT NOT NULL,
    reward INT DEFAULT 0,
    FOREIGN KEY (questionId) REFERENCES test(id)
);