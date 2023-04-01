from tgbot.bot import main
from django.core.management.base import BaseCommand
import os


class Command(BaseCommand):
    help = 'Runs the Telegram bot.'

    def add_arguments(self, parser):
        parser.add_argument('action', choices=['start', 'stop'], help='Action to perform: start or stop')

    def handle(self, *args, **options):
        if options['action'] == 'start':
            if os.environ.get('RUN_MAIN', None) != 'true':
                main()
        elif options['action'] == 'stop':
            print('stop')
