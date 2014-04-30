from django.core.management import call_command, BaseCommand


class Command(BaseCommand):
    help = 'Load data for all apps'

    def handle(self, *args, **options):
        fixtures = (

        )

        for fixture in fixtures:
            print '***** Loading data for %s *****' % fixture
            call_command('loaddata', fixture)
            print '*********** finish ***********'
