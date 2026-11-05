FINDINGS
Things I found while exploring. Raw notes, cleaned up later for the report

---------

ABOUT

Application: a web app for patients to browse available doctors, book appointments on a chosen date and time, see their appointment history and get notifications about upcoming appointments

--------
DB

- One doctor has 11 appointments at the same time. Dr. Mendez, Nov 4 at 09:30, 11 active appointments (one of them is mine). Checked in DBeaver. There are other cases like this too. Need to check if reschedule lets me move into a taken slot

- Some appointments have broken time slots like "25:99", "99:99" or even "invalid timeslot". Looks like the API doesn't check the format

- Some appointments has crazy dates, like year 0123, or 2012 and 2020, and they're still "active". Looks like the API lets you book in the past

- Dr. Sanchez is inactive (retired) but still has future appointments. Checked in DBeaver

- Old appointments never change status. A lot of past appointments are still "active" or "pending" instead of "completed". Can I reschedule an appointment that already happened?

- The database has no rules at all, no relations between tables, nothing stopping duplicates, status and time slot are free text. That's probably why all the stuff above can happen
    - How I'd improve it: the API should validate first, but the database should be the last safety net in case the API misses something
    - A unique index on doctor + date + time slot (only for appointments that are not cancelled) would make double booking impossible, even with a buggy API
    - Foreign keys between appointments, users, doctors and payments, so an appointment can't point to a doctor that doesn't exist
    - Status as a fixed list of values instead of free text (active, pending, completed, cancelled)
    - Time slot stored as a real time type instead of text, so "25:99" can't be saved

- Are thre more people using the db?
- Payments went from 14 to 13 during the same day, while I was running the SQL queries. Not confirmed
- The numbers change during the day. Scheduling conflicts went from 11 to 10 to 9 while I was working

- Payments are marked as "paid", not "completed". The SQL task says "completed payments", so I'll use "paid" and explain why

- Welcome notifications have a date in the future (2027). Small thing, probably bad seed data

- There are appointments on weekends. Not sure if that's allowed, need to see what the app shows for a Saturday

--------
API

- Availability always returns the same 10 slots (09:00 to 15:30) for any doctor and any date, even if the slot is taken. That's probably why double booking happens

- Availability also returns slots for Dr. Sanchez, who is inactive

- Dates come back as "2000-01-01T00:00:00.000Z" (UTC midnight) instead of "2000-01-01" like Swagger says. In GMT-3 that's the day before, which is probably why the day moves back when I schedule

- After rescheduling, updated_at doesn't change, it's still the same as created_at. No way to know when it was changed

- Asking for another patient's appointment (GET /api/appointments/1093) returns 403. Good, that works

- CANCEL DOES NOT SAVE. PUT /cancel answers {"success":true,"status":"cancelled"} and the card changes in the web, but the appointment is still "active" in the API and in the db, even after waiting. Same thing from the web and from the API. The patient thinks they cancelled and the appointment is still there taking the slot. The cancelled appointment I have (1474) came like that from the seed data. Outside the user story but critical

- Reschedule accepts almost anything and saves it, past dates, year 0001, "25:99", a slot with only spaces, "' OR '1'='1", 12:00 (not a slot the doctor offers), a slot already taken by the same doctor

- Reschedule to "2027-02-30" returns 200 and saves March 2. The date rolls over without telling anyone

- The API crashes (500 "Internal server error") instead of rejecting bad input with a 400. Three cases: a date that is not a date ("not-a-date"), a broken JSON body, and an appointment id one above the biggest number a PostgreSQL integer can hold (2147483648, 32 bits). A 500 always means the backend didn't check the input and let it break something inside

- Reschedule with an empty time slot or missing fields returns 400 "appointment_date and time_slot are required". Good, but only an empty string is rejected, spaces pass

- Creating an appointment with the inactive doctor (id 7) works, 201

- Availability without a date also returns the same 10 slots. Availability for a doctor that doesn't exist returns 404, good

- Tried SQL injection on login (' OR '1'='1, ' OR 1=1 --, my email followed by ' --). All of them return 401 "Invalid email or password", same as a wrong password. The backend uses Prisma, which sends values as parameters, so this is expected. Still worth testing on fields that save free text, like time_slot and notes

--------
WEB

- Profile
    - name and last name cannot be edited
    - note added successfully and saved. Tried to change it again, sends PUT but 403 with error message "Name and last name cannot be changed"
    - went back and again to profile and name changed and last name is empty, now after trying to update notes it throws 400 on PUT with error message: "last_name is required"
    - The name lock can be bypassed: my first_name ended up as "Silver Pelican Hi, I am a doctor" with an empty last_name. Now I can't restore it: sending "Silver" / "Pelican" returns 403 "Name and last name cannot be changed", because the API compares against the already modified name. Another candidate's profile shows the same pattern ("Jolly Koala Allergic to penicilin.")
    - REPORT BUG

- Dashboard
    - not being updated after a reschedule, it stays the same. It does update in real time after a cancel, but only on screen, the cancel is never saved (see API)
    - is it necessary to have buttons for browse doctors and new appointment at the top and at the bottom?
    - bell (alerts) from dashboard goes to notifications but bell in the nav bar does nothing

- Doctors
    - It would be better for user experience to click a doctor, click the time I want, click book appointment and automatically fill the fields in the appointments form. This way we can make date and time not editable so users cannot freely pick any date, which seems to be a current bug
    - visually the page looks good and it is responsive, I would change the height of the cards to be the same and get more visual consistency

- Appointments
    - it would be better if users can sort by date ascending or descending, if not, new dates should be at the top for better experience. Currently newer is at the bottom, not a bug but I would report it as an improvement
    - BUG. Users can reschedule once they are completed, it throws success and payload sends date and time
    - BUG, same as above but also with cancelled appointments, this is to be considered, maybe a cancelled one can be rescheduled
    - an appointment can be rescheduled to the past
    - rescheduled appointments are not showing the new schedule
    - nothing changes in real time, I have to reload the page to see changes and clear success messages, this is a bug
    - date can be year 1
    - only cancelled by user can be rescheduled which is fine, but the UI should prevent rescheduling cancelled by doc and completed ones
    - booking, API returns just 201
    - doesn't show the doctor's name, it's not easy to remember who the user has at that time, especially if the user scheduled a month before, cards should include dr name and specialty
    - day is moving back, I schedule for 2/1/1990 and I got 1/1/1990 BUG
    - sort seems to be by creation, it should be either filtered by user, or sorted by next appointment at the top, so users can clearly know what is next
    - users can schedule same time and date with multiple doctors which is not possible since the user can attend one at a time, high bug
    - users can schedule same time and date with the same doctor multiple times, high bug

- Notifications
    - notification card, time and date, time is showing seconds, not necessary and odd, will add it as improvement
    - appointment reminder written as appointment_reminder, not good for users, should be Appointment Reminder
    - not working, scheduled an appointment for tomorrow and it is not showing up in the notifications
    - bell at top right is not triggering anything

- Gear icon, settings, is not triggering anything, maybe it is on purpose for the QA test

