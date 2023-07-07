import factory
from faker import Faker
from django.contrib.auth.models import User
from .models import Ticket, TicketThread, Comment

fake = Faker()

# Factory para criar objetos User


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    # Gera um nome de usuário aleatório
    username = factory.LazyAttribute(lambda _: fake.user_name())
    email = factory.LazyAttribute(
        lambda _: fake.email())  # Gera um email aleatório

# Factory para criar objetos TicketThread


class TicketThreadFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = TicketThread

    # Gera um código de thread sequencial
    thread_code = factory.Sequence(lambda n: f'Thread{n}')
    status = 'A'  # Define o status como "Aberto"

# Factory para criar objetos Ticket


class TicketFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Ticket

    # Cria uma instância de TicketThreadFactory associada ao Ticket
    thread = factory.SubFactory(TicketThreadFactory)
    title = factory.LazyAttribute(
        lambda _: fake.sentence())  # Gera um título aleatório
    # Gera um código de ticket sequencial
    code = factory.Sequence(lambda n: f'Ticket{n}')
    status = 'A'  # Define o status como "Aberto"
    # Gera uma data aleatória dentro desta década
    date = factory.Faker('date_time_this_decade')
    # Gera um corpo de texto aleatório
    body = factory.LazyAttribute(lambda _: fake.text())

# Factory para criar objetos Comment


class CommentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Comment

    # Cria uma instância de TicketFactory associada ao Comment
    ticket = factory.SubFactory(TicketFactory)
    # Cria uma instância de UserFactory associada ao Comment
    user = factory.SubFactory(UserFactory)
    text = "comments"  # Define um texto padrão para o comentário
