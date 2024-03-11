# unChained Meeting Room Reservation System

This is a meeting room reservation system implemented using Django, a high-level Python web framework. This system allows users to reserve meeting rooms for specific dates and times.

## Database Structure

The database structure for this system consists of the following tables:

1. **Room**: This table stores information about the meeting rooms available for reservation. Each room has a unique identifier, name, capacity, and description.

2. **Comment**: This table stores room's comments.

3. **Rating**: This table stores room's ratings.

4. **Reservation**: This table records the reservations made by users. It includes fields such as reservation ID, reserved room ID (foreign key referencing Room table), start and end time of the reservation, the user who made the reservation, and the team for which the reservation was made.

5. **Team**: This table stores team names.

6. **CustomUser**: This table stores user information, including username, email, phone, team ID (foreign key referencing Team table) and any other relevant details.

7. **OTP**: This table stores One-Time Passwords generated for users. It includes user ID (foreign key refrencing CustomUser table), OTP code and created_at time.

### ERD Diagram
![ERD Diagram](https://github.com/ZahraSajadi/django-bootcamp-second-project/blob/develop/erd.png?raw=true)

## How the Program Works

The program provides the following functionalities:

1. **Room Reservation**: Users can view available rooms, check their availability, and reserve a room for a specific date and time.

2. **Reservation Management**: Users can view their existing reservations, and team leaders can cancel them if necessary.

3. **Admin Panel**: Administrators can manage rooms, teams, cancel reservations, and handle user management tasks.

## Requirements

To run this program, you need the following:
- Python (version 3.11)
- PostgreSQL
- Required python packages in `requirements.txt`
    - Django==4.2.11
    - psycopg==3.1.18
    - pillow==10.2.0
    - python-dotenv==1.0.1
    - django-crontab==0.7.1

## Configuration and Running

Follow these steps to configure and run the meeting room reservation system:

1. Clone this repository to your local machine:

```shell
git clone https://github.com/ZahraSajadi/django-bootcamp-second-project
# or
git clone git@github.com:ZahraSajadi/django-bootcamp-second-project.git
```
2. Create a virtual environment (optional but recommended) and activate the environment:

```shell
virtualenv django-env
# and
source django-env/bin/activate
```

3. Navigate to the project directory:
```shell
cd django-bootcamp-second-project.git
```

4. Install the required dependencies using pip:
```shell
pip install -r requirements.txt
```


5. Make a copy of `.env_sample` and rename it to `.env` and edit the configuration as needed.
```env
SECRET_KEY=your_secret_key
DEBUG=True
DB_NAME=unchained
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=localhost
DB_PORT=5432

```
6. Apply database migrations:
```shell
python manage.py makemigrations
python manage.py migrate
```


7. Create a superuser account:
```shell
python manage.py createsuperuser
```

8. Run the command to create groups and permissions:
```shell
python manage.py create_groups_and_permissions
```
9. Start the server:
```
python manage.py runserver
```


10. Access the application in your web browser at `http://127.0.0.1:8000`.

11. When `DEBUG=True`, you can access Django's admin panel, navigate to `http://127.0.0.1:8000/admin` and log in with the superuser credentials created earlier.
      - Necessary management pages apart from Django's admin panels are also implemented and only accessible by users with required permissions regardless of what `DEBUG` is.

## Sending Meetings Email Reminder and Cancellation Email

When a reservation gets removed by an admin or team leader, a cancellation email will be sent to all team mebmers automatically.

In order to send reminder email to team members of meeting that there is less than 2 hours to their meeting you can run the following command.

```shell
python manage.py reservation_email_reminder
```

This command also sends a cancellation email to team members if there is less than 2 hours to their meeting and the room is unavilable (`is_active=False`). An admin can change room status in rooms edit page by setting the `is_active` field.

### Automatic Email Sending
There is also a cron job in `settings.py` that runs the `reservation_email_reminder` command every `59` minutes and stores sent emails in `reminder_email.log` in project root directory.

To add the job to crontab you can run the following command:
```shell
python manage.py crontab add
```
To remove the job you have to run this commands:
```shell
python manage.py crontab remove
```

To change the interval beetween cron job executions you can change it in `settings.py`:
```python
CRONJOBS = [
    (
        "*/59 * * * *",
        "django.core.management.call_command",
        ["reservation_email_reminder"],
        {},
        f">> {REMINDER_EMAIL_LOG_FILE} 2>&1",
    )
]
```
