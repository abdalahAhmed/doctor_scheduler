from datetime import timedelta, date
from .models import Doctor, Clinic, Vacation, Attendance, ScheduleEntry, LocationConfig

WORK_DAYS = ['الأحد', 'الاثنين', 'الثلاثاء', 'الأربعاء', 'الخميس']

def get_upcoming_sunday():
    today = date.today()
    days_until_sunday = (6 - today.weekday()) % 7
    return today + timedelta(days=days_until_sunday)

def get_current_week_start():
    today = date.today()
    days_since_sunday = today.weekday() % 7
    return today - timedelta(days=days_since_sunday)

class DoctorScheduler:
    def __init__(self):
        self.week_start = get_upcoming_sunday()
        self.current_week_start = get_current_week_start()
        self.doctors = list(Doctor.objects.all())
        self.clinics = list(Clinic.objects.all())
        self.active_locations = list(LocationConfig.objects.filter(is_active=True))
        self.vacations = list(Vacation.objects.all())
        self.assignments = {}
        self.doctor_sessions = {doctor.id: 0 for doctor in self.doctors}
        self.assigned_shifts = {}
        self.current_entries = list(ScheduleEntry.objects.filter(week_start_date=self.current_week_start))
        self.last_week_thursday_evening_doctor_ids = self.get_last_week_thursday_evening_doctor_ids()
        self.week_moved = False
        self.week_generated = False

    def get_last_week_thursday_evening_doctor_ids(self):
        entries = ScheduleEntry.objects.filter(
            week_start_date=self.current_week_start,
            day='الخميس',
            session__in=[3, 4]
        )
        return set(entry.doctor.id for entry in entries if entry.doctor)

    def is_doctor_on_vacation(self, doctor, day):
        target_date = self.get_date_from_day(day)
        return any(
            vacation.doctor == doctor and vacation.start_date <= target_date <= vacation.end_date
            for vacation in self.vacations
        )

    def get_date_from_day(self, day):
        days_map = {'الأحد': 0, 'الاثنين': 1, 'الثلاثاء': 2, 'الأربعاء': 3, 'الخميس': 4}
        return self.week_start + timedelta(days=days_map[day])

    def _create_entry(self, doctor, day, session, clinic, week_start):
        ScheduleEntry.objects.create(
            doctor=doctor,
            clinic=clinic,
            day=day,
            session=session,
            week_start_date=week_start
        )
        self.assignments[(doctor.id, day)] = self.assignments.get((doctor.id, day), 0) + 1
        self.doctor_sessions[doctor.id] += 1
        self.assigned_shifts[(doctor.id, day)] = self.assigned_shifts.get((doctor.id, day), []) + [session]

    def _skip_doctor(self, doctor, day, max_sessions_limit, shift, clinic=None, force_max_sessions=False):
        # ✅ منع غير المدربين من عيادات التدريب فقط
        if clinic and clinic.name.strip().lower() in ['trainer', 'or trainer'] and not doctor.has_training:
            print(f"⛔️ {doctor.name} غير مدرب وتم منعه من العيادة {clinic.name}")
            return True

        # ✅ استثناء خاص: منع Dr. Faisal من جلسات المساء يوم الخميس
        if doctor.name == "Dr.Faisal" and day == 'الخميس' and shift == 'ليلي':
            return True

        # التحقق من الأيام غير المتاحة
        if f"{day}-{shift}" in doctor.unavailable_days:
            return True

        # التحقق من الإجازات
        if self.is_doctor_on_vacation(doctor, day):
            return True

        # منع التخصيص أكثر من مرتين في اليوم
        if self.assignments.get((doctor.id, day), 0) >= 2:
            return True

        # منع التجاوز للحد الأقصى للجلسات الأسبوعية إذا لم يتم تجاوز الحد الأقصى
        if not force_max_sessions and self.doctor_sessions.get(doctor.id, 0) >= doctor.max_sessions:
            return True

        # التحقق من الجلسات المخصصة مسبقًا في نفس اليوم
        assigned_sessions = self.assigned_shifts.get((doctor.id, day), [])
        if shift == 'نهاري' and any(s in [1, 2] for s in assigned_sessions):
            return True
        if shift == 'ليلي' and any(s in [3, 4] for s in assigned_sessions):
            return True

        # منع تخصيص الطبيب الذي عمل مساء الخميس في الأسبوع السابق
        if day == 'الخميس' and shift == 'ليلي' and doctor.id in self.last_week_thursday_evening_doctor_ids:
            return True

        return False

    def assign_preferred_doctors(self, day, session, clinic, week_start):
        shift = 'نهاري' if session in [1, 2] else 'ليلي'
        sessions = [1, 2] if shift == 'نهاري' else [3, 4]
        if (shift == 'نهاري' and session != 1) or (shift == 'ليلي' and session != 3):
            return

        doctors_sorted = sorted(self.doctors, key=lambda d: self.doctor_sessions[d.id])
        for doctor in doctors_sorted:
            if self._skip_doctor(doctor, day, doctor.max_sessions, shift, clinic, force_max_sessions=True):
                continue
            if (
                f"{day}-{shift}" in doctor.preferred_days and
                clinic.name in doctor.preferred_clinics
            ):
                for s in sessions:
                    self._create_entry(doctor, day, s, clinic, week_start)
                return

    def assign_neutral_doctors(self, day, session, clinic, week_start):
        shift = 'نهاري' if session in [1, 2] else 'ليلي'
        sessions = [1, 2] if shift == 'نهاري' else [3, 4]
        if (shift == 'نهاري' and session != 1) or (shift == 'ليلي' and session != 3):
            return

        fallback_doctors = []
        doctors_sorted = sorted(self.doctors, key=lambda d: self.doctor_sessions[d.id])
        for doctor in doctors_sorted:
            if self._skip_doctor(doctor, day, doctor.max_sessions, shift, clinic):
                continue
            if f"{day}-{shift}" not in doctor.preferred_days and f"{day}-{shift}" not in doctor.unavailable_days:
                for s in sessions:
                    self._create_entry(doctor, day, s, clinic, week_start)
                return

        for doctor in fallback_doctors:
            if self._skip_doctor(doctor, day, doctor.max_sessions, shift, clinic):
                continue
            for s in sessions:
                self._create_entry(doctor, day, s, clinic, week_start)
            return

        doctors_force_sorted = sorted(self.doctors, key=lambda d: self.doctor_sessions[d.id])
        for doctor in doctors_force_sorted:
            if self._skip_doctor(doctor, day, doctor.max_sessions, shift, clinic, force_max_sessions=True):
                continue
            if f"{day}-{shift}" not in doctor.unavailable_days:
                for s in sessions:
                    self._create_entry(doctor, day, s, clinic, week_start)
                return

    def generate_next_week_schedule(self, manual=False):
        for day in WORK_DAYS:
            for config in self.active_locations:
                clinic = config.clinic
                if day not in clinic.days_available:
                    continue
                sessions = []
                if config.period_1_enabled:
                    sessions.append(1)
                if config.period_2_enabled:
                    sessions.append(2)
                if config.period_3_enabled:
                    sessions.append(3)
                if config.period_4_enabled and not (day == 'الخميس' and config.period_3_enabled):
                    sessions.append(4)

                for session in sessions:
                    self.assign_preferred_doctors(day, session, clinic, self.week_start)

        for day in WORK_DAYS:
            for config in self.active_locations:
                clinic = config.clinic
                if day not in clinic.days_available:
                    continue
                sessions = []
                if config.period_1_enabled:
                    sessions.append(1)
                if config.period_2_enabled:
                    sessions.append(2)
                if config.period_3_enabled:
                    sessions.append(3)
                if config.period_4_enabled and not (day == 'الخميس' and config.period_3_enabled):
                    sessions.append(4)

                for session in sessions:
                    if not ScheduleEntry.objects.filter(
                        week_start_date=self.week_start,
                        clinic=clinic,
                        day=day,
                        session=session
                    ).exists():
                        self.assign_neutral_doctors(day, session, clinic, self.week_start)

        if manual:
            self.week_generated = True

    def move_next_week_to_current(self, manual=False):
        ScheduleEntry.objects.filter(week_start_date=self.current_week_start).delete()
        next_week_entries = ScheduleEntry.objects.filter(week_start_date=self.week_start)
        for entry in next_week_entries:
            ScheduleEntry.objects.create(
                doctor=entry.doctor,
                clinic=entry.clinic,
                day=entry.day,
                session=entry.session,
                week_start_date=self.current_week_start
            )
        next_week_entries.delete()
        if manual:
            self.week_moved = True

    def auto_scheduler_tasks(self):
        today = date.today()
        if today.weekday() == 6 and not self.week_moved:
            self.move_next_week_to_current()
        elif today.weekday() == 1 and not self.week_generated:
            self.generate_next_week_schedule()

    def get_doctor_session_counts(self, week_start):
        counts = {doctor.name: 0 for doctor in self.doctors}
        entries = ScheduleEntry.objects.filter(week_start_date=week_start)
        for entry in entries:
            if entry.doctor:
                counts[entry.doctor.name] += 1
        return counts