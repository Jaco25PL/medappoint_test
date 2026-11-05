
-- Tables: users, doctors, appointments, payments, notifications

----------------------

-- Q1. All my appointments with doctor name, date, time slot and status, newst first
-- The patient is found by email instead of a carcoded id, so the query still works if the db is
-- seeded again and teh id changes
-- time_slot braks the tie when two appoinments are on the same day
-- The email is the test patient account given for this challenge. Change it to run the query for another patient SELECT
    d.first_name || ' ' || d.last_name AS doctor_name,
    a.appointment_date,
    a.time_slot,
    a.status
FROM appointments a
JOIN users u ON u.id = a.patient_id
JOIN doctors d ON d.id = a.doctor_id
WHERE u.email = 'silver.pelican@qa-challenge.com'
ORDER BY a.appointment_date DESC, a.time_slot DESC;


-- Q2. All doctors with their total number of appointments in any status, including doctors with none
-- LEFT JOIN keeps doctors without appointments
-- COUNT(a.id) is used instead of COUNT(*) because a doctor with no appointments still gets one row
-- with NULLs, and COUNT(*) would count it as 1 instead of 0
SELECT
    d.id,
    d.first_name || ' ' || d.last_name AS doctor_name,
    d.is_active,
    COUNT(a.id) AS total_appointments
FROM doctors d
LEFT JOIN appointments a ON a.doctor_id = d.id
GROUP BY d.id, d.first_name, d.last_name, d.is_active
ORDER BY total_appointments DESC;


-- Q3. Future appointments assigned to doctors who are currently inactive
-- CURRENT_DATE is used instead of a fixed date so the query does not go stale
-- All statuses are shown on purpose, the active ones are the real risk, the patient
-- thinks they have an appointment with a doctor who no longer works there

SELECT
    d.first_name || ' ' || d.last_name AS doctor_name,
    a.appointment_date,
    a.status,
    u.first_name || ' ' || u.last_name AS patient_name
FROM appointments a
JOIN doctors d ON d.id = a.doctor_id
JOIN users u ON u.id = a.patient_id
WHERE d.is_active = false
  AND a.appointment_date >= CURRENT_DATE
ORDER BY a.appointment_date;


-- Q4. Scheduling conflicts: same doctor, same date and time slot, more than one appointment
-- HAVING filters the groups after counting (WHERE filters rows before grouping)
-- Cancelled appointments are excluded because a cancellation frees the slot, so it is not a real conflict
-- appointment_ids lists the appointments involved, so each conflict can be checked one by one

SELECT
    d.first_name || ' ' || d.last_name AS doctor_name,
    a.appointment_date,
    a.time_slot,
    COUNT(*) AS appointments_count,
    STRING_AGG(a.id::text, ', ' ORDER BY a.id) AS appointment_ids
FROM appointments a
JOIN doctors d ON d.id = a.doctor_id
WHERE a.status <> 'cancelled'
GROUP BY a.doctor_id, d.first_name, d.last_name, a.appointment_date, a.time_slot
HAVING COUNT(*) > 1
ORDER BY appointments_count DESC, a.appointment_date;


-- Q5. Total revenue collected per doctor (completed payments only) and each doctor s share of the total
-- The question says "completed", but in this database a completed payment is stored as "paid"
-- (it is the only payment status in the table). Filtering by "completed" returns nothing
-- SUM(SUM(p.amount)) OVER () is a window function, it adds up the total of all doctors
-- without collapsing the rows, so each row can be divided by the overall total
-- LEFT JOIN from doctors so doctors with no payments show 0 instead of disappearing
-- The 'paid' filter goes in the ON clause: in WHERE it would drop those doctors again
SELECT
    d.first_name || ' ' || d.last_name AS doctor_name,
    COALESCE(SUM(p.amount), 0) AS total_revenue,
    ROUND(100.0 * COALESCE(SUM(p.amount), 0) / SUM(SUM(p.amount)) OVER (), 2) AS revenue_percentage
FROM doctors d
LEFT JOIN appointments a ON a.doctor_id = d.id
LEFT JOIN payments p ON p.appointment_id = a.id AND p.status = 'paid'
GROUP BY d.id, d.first_name, d.last_name
ORDER BY total_revenue DESC, doctor_name;