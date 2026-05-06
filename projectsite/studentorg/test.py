from django.test import TestCase
from django.core.management import call_command
from io import StringIO
from studentorg.models import College, Program, Organization, Student, OrgMember


# ─────────────────────────────────────────
# MODEL TESTS
# ─────────────────────────────────────────

class CollegeModelTest(TestCase):
    def setUp(self):
        self.college = College.objects.create(college_name="College of Engineering")

    def test_college_created(self):
        self.assertEqual(College.objects.count(), 1)

    def test_college_str(self):
        self.assertEqual(str(self.college), "College of Engineering")

    def test_college_has_timestamps(self):
        self.assertIsNotNone(self.college.created_at)
        self.assertIsNotNone(self.college.updated_at)


class ProgramModelTest(TestCase):
    def setUp(self):
        self.college = College.objects.create(college_name="College of Computing")
        self.program = Program.objects.create(
            prog_name="BS Computer Science",
            college=self.college
        )

    def test_program_created(self):
        self.assertEqual(Program.objects.count(), 1)

    def test_program_str(self):
        self.assertEqual(str(self.program), "BS Computer Science")

    def test_program_linked_to_college(self):
        self.assertEqual(self.program.college, self.college)

    def test_program_deleted_when_college_deleted(self):
        self.college.delete()
        self.assertEqual(Program.objects.count(), 0)


class OrganizationModelTest(TestCase):
    def setUp(self):
        self.college = College.objects.create(college_name="College of Arts")
        self.org = Organization.objects.create(
            name="ACS",
            college=self.college,
            description="Association of Computing Students"
        )

    def test_organization_created(self):
        self.assertEqual(Organization.objects.count(), 1)

    def test_organization_str(self):
        self.assertEqual(str(self.org), "ACS")

    def test_organization_college_nullable(self):
        org_no_college = Organization.objects.create(
            name="SITE",
            college=None,
            description="Society of IT Enthusiasts"
        )
        self.assertIsNone(org_no_college.college)


class StudentModelTest(TestCase):
    def setUp(self):
        self.college = College.objects.create(college_name="College of Computing")
        self.program = Program.objects.create(
            prog_name="BS Information Technology",
            college=self.college
        )
        self.student = Student.objects.create(
            student_id="2024-1-0001",
            lastname="Dela Cruz",
            firstname="Juan",
            middlename="Santos",
            program=self.program
        )

    def test_student_created(self):
        self.assertEqual(Student.objects.count(), 1)

    def test_student_str(self):
        self.assertEqual(str(self.student), "Dela Cruz, Juan")

    def test_student_middlename_optional(self):
        student2 = Student.objects.create(
            student_id="2024-1-0002",
            lastname="Reyes",
            firstname="Maria",
            program=self.program
        )
        self.assertIsNone(student2.middlename)

    def test_student_deleted_when_program_deleted(self):
        self.program.delete()
        self.assertEqual(Student.objects.count(), 0)


class OrgMemberModelTest(TestCase):
    def setUp(self):
        self.college = College.objects.create(college_name="College of Computing")
        self.program = Program.objects.create(
            prog_name="BS Computer Science",
            college=self.college
        )
        self.student = Student.objects.create(
            student_id="2024-1-0001",
            lastname="Dela Cruz",
            firstname="Juan",
            program=self.program
        )
        self.org = Organization.objects.create(
            name="ACS",
            college=self.college,
            description="Association of Computing Students"
        )
        self.membership = OrgMember.objects.create(
            student=self.student,
            organization=self.org,
            date_joined="2023-06-01"
        )

    def test_membership_created(self):
        self.assertEqual(OrgMember.objects.count(), 1)

    def test_membership_linked_correctly(self):
        self.assertEqual(self.membership.student, self.student)
        self.assertEqual(self.membership.organization, self.org)

    def test_membership_deleted_when_student_deleted(self):
        self.student.delete()
        self.assertEqual(OrgMember.objects.count(), 0)

    def test_membership_deleted_when_org_deleted(self):
        self.org.delete()
        self.assertEqual(OrgMember.objects.count(), 0)


# ─────────────────────────────────────────
# MANAGEMENT COMMAND TESTS
# ─────────────────────────────────────────

class CreateInitialDataCommandTest(TestCase):
    def setUp(self):
        # Seed required data before running the command
        self.college = College.objects.create(college_name="College of Computing")
        self.program = Program.objects.create(
            prog_name="BS Computer Science",
            college=self.college
        )

    def test_command_creates_organizations(self):
        out = StringIO()
        call_command('create_initial_data', stdout=out)
        self.assertGreater(Organization.objects.count(), 0)

    def test_command_creates_students(self):
        out = StringIO()
        call_command('create_initial_data', stdout=out)
        self.assertGreater(Student.objects.count(), 0)

    def test_command_creates_memberships(self):
        out = StringIO()
        call_command('create_initial_data', stdout=out)
        self.assertGreater(OrgMember.objects.count(), 0)

    def test_command_output_messages(self):
        out = StringIO()
        call_command('create_initial_data', stdout=out)
        output = out.getvalue()
        self.assertIn('Organizations created.', output)
        self.assertIn('Students created.', output)
        self.assertIn('Memberships created.', output)

    def test_command_fails_gracefully_without_programs(self):
        # Delete programs to simulate missing data
        Program.objects.all().delete()
        out = StringIO()
        call_command('create_initial_data', stdout=out)
        # Students should NOT be created
        self.assertEqual(Student.objects.count(), 0)