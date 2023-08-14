from unibilim.meetings.models import Meetings
from django.conf import settings

def main():
    print(settings.DEBUG)

    links = Meetings.objects.all()
    for link in links:
        print(link.url)

if __name__ == "__main__":
    main()
