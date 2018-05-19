import os
import json
import shutil

from django.core.files import File
from django.core.management.base import BaseCommand
from django.db import transaction

from .helpers.categories_mapper import mapper
from ...models import Book, Author, Category, Language, TheUser
from app.tasks import compress_pdf_task
from app.utils import resize_image

MAX_AUTHOR_NAME_LENGTH = 96
MAX_BOOK_NAME_LENGTH = 146
MAX_DESCRIPTION_LENGTH = 996

BOOK_COVER_HEIGHT = 350


# ----------------------------------------------------------------------------------------------------------------------
class Command(BaseCommand):
    help = 'Uploads the books to the server.'

    def add_arguments(self, parser):
        parser.add_argument('--path',
                            type=str,
                            help='The path to the folder from where to get data')

    def handle(self, *args, **options):
        print('Start processing...')
        current_iteration = 1

        for root, dirs, files in os.walk(options['path']):
            if current_iteration > 1:
                print('Folder "{}" processing'.format(root))
                
                with open('{}/{}'.format(root, 'meta.json')) as json_file:
                    data = json.loads(json_file.read())

                    book_path = None
                    book_cover = None
                    for filename in files:
                        if filename.endswith('.pdf'):
                            book_path = '{}/{}'.format(root, filename)
                        if filename.endswith('.png'):
                            book_cover = '{}/{}'.format(root, filename)

                    self.prepare_meta(data)

                    with transaction.atomic():
                        author = self.get_author(data)
                        category = self.get_category(data)

                        book = Book.objects.create(
                            book_name=data['name'],
                            id_author=author,
                            id_category=category,
                            description=data['description'],
                            language=Language.objects.get(id=1),
                            who_added=TheUser.objects.get(id=1)
                        )
                        book.book_file.save(os.path.basename(book_path), File(open(book_path, 'rb')))
                        if book_cover:
                            book.photo.save(os.path.basename(book_cover), File(open(book_cover, 'rb')))
                            resize_image(book.photo.path, BOOK_COVER_HEIGHT)

                        book.save()

                        compress_pdf_task.delay(book.book_file.path, book.id)

                        print('Book with ID: "{}" name: "{}" uploaded successfully!'.format(
                            book.id, book.book_name))

                        shutil.rmtree(root)

            current_iteration += 1
            print('Processed books: ' + str(current_iteration))

    def prepare_meta(self, data):
        if len(data['author']) > MAX_AUTHOR_NAME_LENGTH:
            data['author'] = data['author'][:MAX_AUTHOR_NAME_LENGTH - 1] + '...'

        if len(data['name']) > MAX_BOOK_NAME_LENGTH:
            data['name'] = data['name'][:MAX_BOOK_NAME_LENGTH - 1] + '...'

        if len(data['description']) > MAX_DESCRIPTION_LENGTH:
            data['description'] = data['description'][:MAX_DESCRIPTION_LENGTH - 1] + '...'

        data['category'] = mapper[data['category']]

    def get_author(self, data):
        author = Author.objects.filter(author_name=data['author'])

        if not author:
            author = Author.objects.create(author_name=data['author'])
        else:
            author = author[0]

        return author

    def get_category(self, data):
        return Category.objects.get(category_name=data['category'])


