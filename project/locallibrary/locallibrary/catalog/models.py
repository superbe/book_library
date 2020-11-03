from django.db import models
from django.urls import reverse
import uuid
from django.contrib.auth.models import User
from datetime import date


class Genre(models.Model):
    """
    Модель, представляющая жанр книги (например, научная фантастика, научно-популярная литература).
    """
    name = models.CharField(max_length=200,
                            help_text="Укажите жанр книги (например, научная фантастика, французская поэзия и т. д.)")

    def __str__(self):
        """
        Строка для представления объекта модели (на сайте администратора и т. д.)
        """
        return self.name


class Language(models.Model):
    """
    Модель, представляющая язык книги.
    """
    name = models.CharField(max_length=200,
                            help_text="Укажите язык книги (например, английский, русский и т. д.)")

    def __str__(self):
        """
        Строка для представления объекта модели (на сайте администратора и т. д.)
        """
        return self.name


class Book(models.Model):
    """
    Модель, представляющая книгу (но не конкретный экземпляр книги).
    """
    title = models.CharField(max_length=200)
    author = models.ForeignKey('Author', on_delete=models.SET_NULL, null=True)
    # Используется внешний ключ, потому что у книги может быть только один автор, но у авторов может быть несколько книг
    # Автор как строка, а не объект, потому что он еще не объявлен в файле.
    summary = models.TextField(max_length=1000, help_text="Введите краткое описание книги")
    isbn = models.CharField('ISBN', max_length=13,
                            help_text='13 символов <a href="https://www.isbn-international.org/content/what-isbn">номер ISBN</a>')
    genre = models.ManyToManyField(Genre, help_text="Выберите жанр для этой книги")
    language = models.ManyToManyField(Language, help_text="Выберите язык этой книги")

    # ManyToManyField используется, потому что жанр может содержать много книг. Книги могут охватывать многие жанры.
    # Класс жанра уже определен, поэтому мы можем указать объект выше.

    def __str__(self):
        """
        Строка для представления объекта модели.
        """
        return self.title

    def get_absolute_url(self):
        """
        Возвращает URL-адрес для доступа к конкретному экземпляру книги.
        """
        return reverse('book-detail', args=[str(self.id)])

    def display_genre(self):
        """
        Создает строку для жанра. Это необходимо для отображения жанра в админке.
        """
        return ', '.join([genre.name for genre in self.genre.all()[:3]])

    display_genre.short_description = 'Genre'


class BookInstance(models.Model):
    """
    Модель, представляющая конкретный экземпляр книги, который можно взять из библиотеки.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4,
                          help_text="Уникальный идентификатор этой книги в библиотеке")
    book = models.ForeignKey('Book', on_delete=models.SET_NULL, null=True)
    imprint = models.CharField(max_length=200)
    due_back = models.DateField(null=True, blank=True)

    LOAN_STATUS = (
        ('m', 'Обслуживание'),
        ('o', 'На руках'),
        ('a', 'Имеется в наличии'),
        ('r', 'Зарезервирована'),
    )

    status = models.CharField(max_length=1, choices=LOAN_STATUS, blank=True, default='m', help_text='Наличие книги')
    borrower = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    @property
    def is_overdue(self):
        if self.due_back and date.today() > self.due_back:
            return True
        return False

    class Meta:
        ordering = ["due_back"]
        permissions = (("can_mark_returned", "Установить книгу как возвращенную"),)

    def __str__(self):
        """
        String for representing the Model object
        """
        return f'{self.id} ({self.book.title})'


class Author(models.Model):
    """
    Модель, представляющая автора.
    """
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    date_of_birth = models.DateField(null=True, blank=True)
    date_of_death = models.DateField('Died', null=True, blank=True)

    def get_absolute_url(self):
        """
        Возвращает URL-адрес для доступа к конкретному экземпляру автора.
        """
        return reverse('author-detail', args=[str(self.id)])

    def __str__(self):
        """
        Строка для представления объекта модели.
        """
        return f'{self.last_name}, {self.first_name}'

    class Meta:
        ordering = ['last_name']
