from unittest.mock import MagicMock, patch

import pretix_esncard.helpers as helpers
from pretix_esncard.models import ESNCardEntry

# ---------------------------
# Fake objects for testing
# ---------------------------


class FakeAnswer:
    def __init__(self, identifier, answer):
        self.question = MagicMock(identifier=identifier)
        self.answer = answer

    def delete(self):
        self.deleted = True


class FakePosition:
    def __init__(self, name, answers):
        self.attendee_name = name
        self.answers = MagicMock()
        self.answers.all.return_value = answers


def make_entry(card_number, name="Test User", status=None, duplicate=False):
    entry = ESNCardEntry(
        position=MagicMock(),
        answer=MagicMock(),
        card_number=card_number,
        name=name,
    )
    entry.status = status
    entry.duplicate = duplicate
    return entry


# ---------------------------
# get_esncard_answers
# ---------------------------


def test_get_esncard_answers_filters_correctly():
    pos = FakePosition(
        name="Alice",
        answers=[
            FakeAnswer("esncard", " abcd123 "),
            FakeAnswer("other", "ignored"),
        ],
    )

    result = helpers.get_esncard_answers([pos])

    assert len(result) == 1
    entry = result[0]
    assert entry.card_number == "ABCD123"
    assert entry.name == "Alice"


# ---------------------------
# populate_cards
# ---------------------------


def test_populate_cards_populates_fields():
    entry = make_entry("ABC123")

    fake_api_data = {
        "status": "active",
        "expiration-date": "2025-12-31",
    }

    with patch("pretix_esncard.helpers.fetch_card", return_value=fake_api_data):
        helpers.populate_cards([entry])

    assert entry.status == "active"
    assert entry.expiration_date == "2025-12-31"
    assert entry.raw_api_data == fake_api_data


def test_populate_cards_handles_not_found():
    entry = make_entry("ABC123")

    with patch("pretix_esncard.helpers.fetch_card", return_value=None):
        helpers.populate_cards([entry])

    assert entry.status == "not found"


# ---------------------------
# check_duplicates
# ---------------------------


def test_check_duplicates_marks_duplicates():
    a = make_entry("X1")
    b = make_entry("X1")
    c = make_entry("X2")

    helpers.is_duplicate([a, b, c])

    assert a.duplicate is True
    assert b.duplicate is True
    assert c.duplicate is False


# ---------------------------
# delete_wrong_answers
# ---------------------------


def test_delete_wrong_answers_deletes_non_active():
    a = make_entry("X1", status="expired")
    b = make_entry("X2", status="active")

    a.answer.delete = MagicMock()
    b.answer.delete = MagicMock()

    helpers.delete_wrong_answers([a, b])

    a.answer.delete.assert_called_once()
    b.answer.delete.assert_not_called()


# ---------------------------
# generate_error_message
# ---------------------------


def test_generate_error_message_no_errors():
    entries = [make_entry("X1", status="active")]
    msg = helpers.generate_error_message(entries)
    assert msg == ""


def test_generate_error_message_not_found():
    e = make_entry("X1", name="Alice", status="not found")
    msg = helpers.generate_error_message([e])
    assert "does not exist" in msg
    assert "X1 (Alice)" in msg


def test_generate_error_message_duplicate():
    e1 = make_entry("X1", status="active", duplicate=True)
    e2 = make_entry("X1", status="active", duplicate=True)

    msg = helpers.generate_error_message([e1, e2])
    assert "used more than once" in msg


def test_generate_error_message_expired():
    e = make_entry("X1", name="Alice", status="expired")
    e.expiration_date = "2024-01-01"

    msg = helpers.generate_error_message([e])
    assert "expired on 2024-01-01" in msg


def test_generate_error_message_available():
    e = make_entry("X1", name="Alice", status="available")
    msg = helpers.generate_error_message([e])
    assert "has not been registered yet" in msg


def test_generate_error_message_invalid():
    e = make_entry("X1", name="Alice", status="weird")
    msg = helpers.generate_error_message([e])
    assert "is invalid" in msg
