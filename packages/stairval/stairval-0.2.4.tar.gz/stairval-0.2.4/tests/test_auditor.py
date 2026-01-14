import pytest
import io
import os


from .simple import Person, Address, PersonAuditor, AddressAuditor


class TestAuditor:
    @pytest.fixture(scope="class")
    def auditor(self) -> PersonAuditor:
        return PersonAuditor(
            address_auditor=AddressAuditor(),
        )

    def test_ok_person(
        self,
        auditor: PersonAuditor,
    ):
        person = Person(
            name="Jack Black",
            age=43,
            address=Address(
                street="331 Farmington Ave",
                city="West Hartford",
                zip_code="06119",
                country="United States of America",
            ),
        )

        notepad = auditor.prepare_notepad("person")
        auditor.audit(person, notepad)

        buf = io.StringIO()
        notepad.summarize(file=buf)

        assert buf.getvalue() == "No errors or warnings were found" + os.linesep

    def test_few_errors(
        self,
        auditor: PersonAuditor,
    ):
        person = Person(
            name="Crooked Joe",
            age=-9,
            address=Address(
                street="",
                city="West Hartford",
                zip_code="-12345",
                country="United States of America",
            ),
        )

        notepad = auditor.prepare_notepad("person")
        auditor.audit(person, notepad)

        actual = notepad.summary().split(os.linesep)

        expected = [
            "Showing errors and warnings",
            "▸ person",
            "    errors:",
            "    • `age` must not be negative",
            "  ▸ address",
            "      errors:",
            "      • `zip_code` must not be negative",
            "      warnings:",
            "      • `street` should not be empty",
            "",
        ]
        assert actual == expected
