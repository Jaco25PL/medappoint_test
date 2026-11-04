FINDINGS
Things I found while exploring. Raw notes, cleaned up later for the report

--------
DB

- One doctor has 11 appointments at the same time. Dr. Mendez, Nov 4 at 09:30, 11 active appointments (one of them is mine). Checked in DBeaver. There are other cases like this too. Need to check if reschedule lets me move into a taken slot.

- Some appointments have broken time slots like "25:99", "99:99" or even "invalid timeslot". Looks like the API doesn't check the format.

- Some appointments have crazy dates, like year 0123, or 2012 and 2020, and they're still "active". Looks like the API lets you book in the past.

- Dr. Sánchez is inactive (retired) but still has future appointments. Checked in DBeaver.

- Old appointments never change status. A lot of past appointments are still "active" or "pending" instead of "completed". Can I reschedule an appointment that already happened?

- The database has no rules at all: no relations between tables, nothing stopping duplicates, status and time slot are free text. That's probably why all the stuff above can happen.

- Payments are marked as "paid", not "completed". The SQL task says "completed payments", so I'll use "paid" and explain why.

- Welcome notifications have a date in the future (2027). Small thing, probably bad seed data.

- There are appointments on weekends. Not sure if that's allowed, need to see what the app shows for a Saturday.

--------
WEB

- Profile
    - name and last name cannot be edited.
    - note added successfully and saved. Tried to change it again, sends a PUT but 403 with error message "Name and last name cannot be changed".
    - went back and again to profile and name changed and last name is empty, now after trying to update notes it throws 400 on PUT with error message: "last_name is required"
    - The name lock can be bypassed: my first_name ended up as "Silver Pelican Hi, I am a doctor" with an empty last_name. Now I can't restore it: sending "Silver" / "Pelican" returns 403 "Name and last name cannot be changed", because the API compares against the already modified name. Another candidate's profile shows the same pattern ("Jolly Koala Allergic to penicilin.")
    - REPORT BUG

- Dashboard
    - not being updated with the new appointments, it is fixed
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
