import factory
from faker import Faker
from django.contrib.auth.models import User
from .models import Ticket, TicketThread, Comment

fake = Faker()

class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    username = factory.LazyAttribute(lambda _: fake.user_name())
    email = factory.LazyAttribute(lambda _: fake.email())

class TicketThreadFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = TicketThread

    thread_code = factory.Sequence(lambda n: f'Thread{n}')
    status = 'A'

class TicketFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Ticket

    thread = factory.SubFactory(TicketThreadFactory)
    title = factory.LazyAttribute(lambda _: fake.sentence())
    code = factory.Sequence(lambda n: f'Ticket{n}')
    status = 'A'
    body = factory.LazyAttribute(lambda _: fake.text())

class CommentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Comment

    ticket = factory.SubFactory(TicketFactory)
    user = factory.SubFactory(UserFactory)
    text = "comments"
