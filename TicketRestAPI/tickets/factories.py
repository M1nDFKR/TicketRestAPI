# myapp/factories.py
import factory
from faker import Faker
from .models import Ticket, TicketThread, Comment, User

fake = Faker()

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
    user = factory.SubFactory(User)
    text = "Exemplo de texto do comentário"   
