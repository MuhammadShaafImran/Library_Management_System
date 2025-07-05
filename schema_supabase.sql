-- ENUM Types for dropdowns
CREATE TYPE user_type_enum AS ENUM ('student', 'teacher', 'librarian','guest');
CREATE TYPE user_status_enum AS ENUM ('active', 'inactive', 'banned');
CREATE TYPE storage_type_enum AS ENUM ('online', 'offline');
CREATE TYPE borrow_status_enum AS ENUM ('pending', 'approved', 'rejected');

-- Users Table
CREATE TABLE users (
  id int GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  name text NOT NULL,
  password text NOT NULL,
  type user_type_enum NOT NULL,
  email text UNIQUE NOT NULL,
  phone text UNIQUE,
  status user_status_enum NOT NULL,
  last_login date,
  joining_date date NOT NULL
);

-- Students Table
CREATE TABLE students (
  id int PRIMARY KEY REFERENCES users(id),
  rollno int UNIQUE NOT NULL,
  department text NOT NULL,
  batch int NOT NULL,
  semester int NOT NULL
);

-- Teachers Table
CREATE TABLE teachers (
  id int PRIMARY KEY REFERENCES users(id),
  department text NOT NULL,
  designation text NOT NULL
);

-- Librarians Table
CREATE TABLE librarians (
  id int PRIMARY KEY REFERENCES users(id),
  admin boolean DEFAULT false
);

-- Categories Table
CREATE TABLE categories (
  id int GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  name text UNIQUE NOT NULL,
  description text NOT NULL,
  created_at date NOT NULL
);

-- Books Table
CREATE TABLE books (
  id int GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  category_id int REFERENCES categories(id),
  title text NOT NULL,
  isbn text UNIQUE,
  author text NOT NULL,
  publisher text NOT NULL,
  published_year int NOT NULL,
  language text NOT NULL,
  cover_image text,
  tags text,
  storage_type storage_type_enum NOT NULL
  added_by int REFERENCES users(id),
);

-- Online Books
CREATE TABLE book_online (
  id int PRIMARY KEY REFERENCES books(id),
  address text NOT NULL,
  platform_name text NOT NULL,
  access_url text NOT NULL,
  format text NOT NULL
);

-- Offline Books
CREATE TABLE book_offline (
  id int PRIMARY KEY REFERENCES books(id),
  quantity int NOT NULL,
  address text NOT NULL,
  shelf_no text NOT NULL,
  room text NOT NULL
);

-- Borrow Table
CREATE TABLE borrow (
  id int GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  user_id int REFERENCES users(id),
  book_id int REFERENCES books(id),
  request_description text,
  current_date date NOT NULL,
  return_date date,
  fine numeric DEFAULT 0,
  approved_by int REFERENCES users(id),
  approved_date date,
  return_condition text,
  status borrow_status_enum DEFAULT 'pending',
  reminder_sent boolean DEFAULT false
);

-- Fine Table
CREATE TABLE fines (
  id int GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  borrow_id int REFERENCES borrow(id),
  amount numeric NOT NULL,
  paid boolean DEFAULT false,
  paid_date date,
  payment_method text,
  reason text,
  created_at date NOT NULL
);

-- Record Table
CREATE TABLE records (
  id int GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  user_id int REFERENCES users(id),
  action text NOT NULL,
  book_id int REFERENCES books(id),
  borrow_id int REFERENCES borrow(id),
  timestamp date NOT NULL,
  ip_address text,
  device_info text,
  created_by int REFERENCES users(id),
  action_details text
);
