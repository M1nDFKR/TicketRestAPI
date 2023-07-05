import factory
from faker import Faker
from django.contrib.auth.models import User
from .models import Ticket, TicketThread, Comment

fake = Faker()

# Factory para criar objetos User
class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    username = factory.LazyAttribute(lambda _: fake.user_name())  # Gera um nome de usuário aleatório
    email = factory.LazyAttribute(lambda _: fake.email())  # Gera um email aleatório

# Factory para criar objetos TicketThread
class TicketThreadFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = TicketThread

    thread_code = factory.Sequence(lambda n: f'Thread{n}')  # Gera um código de thread sequencial
    status = 'A'  # Define o status como "Aberto"

# Factory para criar objetos Ticket
class TicketFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Ticket

    thread = factory.SubFactory(TicketThreadFactory)  # Cria uma instância de TicketThreadFactory associada ao Ticket
    title = factory.LazyAttribute(lambda _: fake.sentence())  # Gera um título aleatório
    code = factory.Sequence(lambda n: f'Ticket{n}')  # Gera um código de ticket sequencial
    status = 'A'  # Define o status como "Aberto"
    body = factory.LazyAttribute(lambda _: fake.text())  # Gera um corpo de texto aleatório

# Factory para criar objetos Comment
class CommentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Comment

    ticket = factory.SubFactory(TicketFactory)  # Cria uma instância de TicketFactory associada ao Comment
    user = factory.SubFactory(UserFactory)  # Cria uma instância de UserFactory associada ao Comment
    text = "comments"  # Define um texto padrão para o comentário
