from unittest.mock import patch

import pytest
from pretix.base.models import CartPosition, Event, Item, Organizer, Question
from pretix.base.services.cart import CartError
from pretix.base.signals import validate_cart


@pytest.mark.django_db
def test_esncard_validate_cart_invalid_card():
    """
    Integration test:
    - Create real Pretix objects
    - Attach an ESNcard answer
    - Mock the ESNcard API to return 'not found'
    - Ensure the signal raises CartError with the correct message
    """

    # ---------------------------
    # Setup Pretix objects
    # ---------------------------
    organizer = Organizer.objects.create(name="TestOrg", slug="testorg")
    event = Event.objects.create(
        organizer=organizer,
        name="TestEvent",
        slug="testevent",
        date_from="2030-01-01",
    )

    item = Item.objects.create(event=event, name="Ticket", default_price=10)

    # Create a question with identifier "esncard"
    question = Question.objects.create(
        event=event,
        question="ESNcard number",
        type="S",
        identifier="esncard",
    )

    # Create a cart position
    pos = CartPosition.objects.create(
        event=event,
        item=item,
        price=10,
        cart_id="abc123",
    )

    # Attach an answer to the position
    pos.answers.create(
        question=question,
        answer="ABC123",
    )

    # ---------------------------
    # Mock the ESNcard API
    # ---------------------------
    with patch("pretix_esncard.signals.populate_cards") as mock_populate:
        # Simulate API returning "not found"
        def fake_populate(cards):
            cards[0].status = "not found"

        mock_populate.side_effect = fake_populate

        # ---------------------------
        # Trigger the signal
        # ---------------------------
        with pytest.raises(CartError) as exc:
            validate_cart.send(sender=event, positions=[pos])

    # ---------------------------
    # Assertions
    # ---------------------------
    msg = str(exc.value)
    assert "does not exist" in msg
    assert "ABC123" in msg
