# Modern Application Development I

## Project Statement: Quiz Master - V1

It is a multi-user app (one requires an administrator and other users) that acts as an exam preparation site for multiple courses.

## Frameworks to be Used

These are the mandatory frameworks on which the project has to be built:


- Flask for application back-end.
- Jinja2 templating, HTML, CSS and Bootstraps for application front-end.
- SQLite for database (No other database is permitted).
## Roles

The platform will have *two* roles:


1. Admin - root access - It is the superuser of the app and requires no registration

- Admin is also known as the quiz master
- There is only one admin to this application
- The administrator login redirects to the quiz master/admin dashboard
- The administrator will manage all the other users
- The administrator will create a new subject
- The administrator will add various chapters under a subject
- The administrator will add quiz questions under a chapter

2. User - Can attempt any quiz of its choice.

- User Registration and Login
- Each user may have:
    - id - primary key
    - Username (email)
    - Password
    - Full Name
    - Qualification
    - DOB
- To be able to choose the subject as well as the chapter name
- Start the quiz
- View the quiz scores
## Terminologies

**User**: The user will register/login and attempt any quiz of his/her interest.
Terminologies

User: The user will register/login and attempt any quiz of his/her interest.


Admin: The superuser with full control over other users and data. Registration is not allowed for the admin: The admin account must pre-exist in the database when the application is initialized.


Subject: The field of study in which the user wishes to give the quiz. The admin will be creating one or many subjects in the application. Every subject can possibly have the following fields:

- id - primary key
- Name
- Description
- etc: Additional fields (if any)

Chapter: Each subject can be subdivided into multiple modules called chapters. The possible fields of a chapter can be the following:

- id - primary key
- Name
- Description
- etc: Additional fields (if any)

Quiz: A quiz is a test that is used to evaluate the user’s understanding of any particular chapter of any particular subject. A test may contain the following attributes:


- id - primary key
- chapter_id (foreign key-chapter)
- date_of_quiz
- time_duration(hh:mm)
- remarks (if any)
- etc: Additional fields (if any)
Questions: Every quiz will have a set of questions created by the admin. Possible fields for a question include:

- id - primary key
- quiz_id (foreign key-quiz)
- question_statement
- Option1, option2, … etc.
- etc: Additional fields (if any)

Scores: Stores the scores and details of a user's quiz attempt. Possible fields for scores include:

- id - primary key
- quiz_id (foreign key-quiz)
- user_id (foreign key-user)
- time_stamp_of_attempt
- total_scored
## Application Wireframe: Quiz Master
 (wireframe is in directory)

Note:
The provided wireframe is intended only to illustrate the application's flow and demonstrate what should appear when a user navigates between pages.

- Replication of the exact views is NOT mandatory.
- Students are encouraged to work on their own front-end ideas and designs while maintaining the application's intended functionality and flow.

## Core Functionalities

1. Admin Login and User Login
- A login/register form with fields like username, password etc. for user and admin login
- You can either use a proper login framework or just use a simple HTML form with username and password (we are not concerned with how secure the login or the app is)
- The app must have a suitable model to store and differentiate all types of users

2. Admin Dashboard - for the Admin

- The admin should be added, whenever a new database is created
- The admin creates/edits/deletes a subject
- The admin creates/edits/deletes a chapter under the subject
- The admin will create a new quiz under a chapter
- Each quiz contains a set of questions (MCQ - only one option correct)
- The admin can search the users/subjects/quizzes
- Shows the summary charts

3. Quiz management - for the Admin

- Edit/delete a quiz
- The admin specifies the date and duration(HH: MM) of the quiz
- The admin creates/edits/deletes the MCQ (only one option correct) questions inside the specific quiz

4. User dashboard - for the User

- The user can attempt any quiz of his/her interest
- Every quiz has a timer (timer is optional)
- Each quiz score is recorded
- The earlier quiz attempts are shown
- Shows the summary charts
Note: The database must be created programmatically (via table creation or model code). Manual database creation, such as using DB Browser for SQLite, is NOT allowed.

## Recommended Functionalities

- API resources are created to interact with the subjects, chapters, and/or quizzes. (Please note: you can choose which API resources to make from the given ones. It is NOT mandatory to create API resources for CRUD of all the components.)
- APIs can either be created by returning JSON from a controller or using a flask extension like flask_restful
- External APIs/libraries for creating charts, e.g. Chart JS
- Implementing frontend validation on all the form fields using HTML5 form validation or JavaScript
- Implement backend validation within your app's controllers.
## Optional Functionalities

- Provide styling and aesthetics to your application by creating a beautiful and responsive front end using simple CSS or Bootstrap.
- Incorporate a proper login system to prevent unauthorized access to the app using Flask extensions like flask_login, flask_security etc.
- Any additional feature you feel is appropriate for the application
Evaluation




## Milestones

### Core Requirements (Milestones 1-7)

#### Milestone 1: Database Models and Schema Setup
✅ Expected Time: 5-7 days  
📊 Completion Progress: 15%

- Define tables for User, Admin, Subject, Chapter, Quiz, Question, Score, etc., in SQLite.
- Set up relationships between tables (e.g., Subjects have multiple Chapters, Quizzes belong to Chapters).
- Ensure the database is programmatically created through a Python script/file.  
**Git Commit Message:** Created database schema for users, subjects, quizzes, and scores

#### Milestone 2: Authentication and Role Management
✅ Expected Time: 5 days  
📊 Completion Progress: 10%

- Create an Admin login (Admin is predefined, no registration allowed).
- Implement User registration and login with required fields (username (email), password, full name, etc.).
- Users should be redirected to their respective dashboards after login.  
**Git Commit Message:** Implemented user registration and admin login functionality

#### Milestone 3: Admin Dashboard and Management
✅ Expected Time: 7-9 days  
📊 Completion Progress: 20%

- Admin should be able to:
    - Create/Edit/Delete Subjects.
    - Create/Edit/Delete Chapters under a subject.
    - Create/Edit/Delete Quizzes under a chapter.
    - Create/Edit/Delete Questions under a quiz.
- Admin should see a list of all users and their details.  
**Git Commit Message:** Built Admin dashboard with CRUD operations for subjects, chapters, quizzes, and questions

#### Milestone 4: User Dashboard and Quiz Attempt System
✅ Expected Time: 7 days  
📊 Completion Progress: 15%

- Users should see a list of available subjects and quizzes.
- Users should be able to attempt a quiz (MCQ format with one correct option).
- Implement a timer for each quiz.
- Users should get feedback on correct/incorrect answers after the quiz.
- Store quiz scores in the database.  
**Git Commit Message:** Developed User dashboard with quiz attempt functionality and timer

#### Milestone 5: Score Management and Quiz Result Display
✅ Expected Time: 5 days  
📊 Completion Progress: 15%

- Store quiz scores after submission.
- Users should see past quiz attempts and scores.
- Display a quiz summary report with total scores.  
**Git Commit Message:** Implemented score tracking and quiz result display

#### Milestone 6: Search Functionality for Admin and Users
✅ Expected Time: 4 days  
📊 Completion Progress: 10%

- **Admin Search:** Admin can search for users, subjects, quizzes, and questions.
- **User Search:** Users can search for subjects and quizzes.  
**Git Commit Message:** Added search functionality for Admin and Users

#### Milestone 7: Quiz Time and Duration Management
✅ Expected Time: 4 days  
📊 Completion Progress: 10%

- Admin should set date and time duration (HH:MM) when creating a quiz.
- Users should only be able to attempt quizzes within the given timeframe.  
**Git Commit Message:** Implemented quiz scheduling with time duration

### Recommended Functionalities (Milestones 8-9)

#### Milestone 8: API Development for Data Access
✅ Expected Time: 7 days

- Develop API endpoints to fetch subjects, chapters, quizzes, and scores.
- Ensure APIs return JSON responses.  
**Git Commit Message:** Created API endpoints for subjects, quizzes, and scores

#### Milestone 9: Summary Charts and Data Visualization
✅ Expected Time: 5 days

- Display quiz performance charts for users.
- Admin should see summary statistics of quizzes and users.  
**Git Commit Message:** Added summary charts for quiz statistics and user performance

### Optional Enhancements (Milestones 10-11)

#### Milestone 10: Frontend Enhancements and UI Improvements
✅ Expected Time: 7-9 days

- Enhance the UI using Bootstrap and CSS, implement frontend validation for forms, and ensure the app is mobile-responsive.  
**Git Commit Message:** Enhanced UI with Bootstrap styling and form validation

#### Milestone 11: Security Enhancements and Final Testing
✅ Expected Time: 7 days

- Implement backend validation for form inputs.
- Perform final testing to fix any bugs or security loopholes.
- Ensure all routes are protected based on user roles.  
**Git Commit Message:** Enhanced security with backend validation and finalized testing

