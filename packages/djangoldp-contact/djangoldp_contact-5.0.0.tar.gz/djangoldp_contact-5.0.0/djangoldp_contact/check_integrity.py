from django.conf import settings
from django.contrib.auth import get_user_model
from djangoldp_contact.models import Contact
from djangoldp.check_integrity import is_alive
from urllib.parse import urlparse

def add_arguments(parser):
  parser.add_argument(
    "--ignore-contact-members",
    default=False,
    nargs="?",
    const=True,
    help="Ignore contact members related check",
  )

def check_integrity(options):
  print('---')
  print("DjangoLDP Contact")
  if(not options["ignore_contact_members"]):
    ignored = set()
    if(options["ignore"]):
      for target in options["ignore"].split(","):
        ignored.add(urlparse(target).netloc)

    resources_404 = set()
    resources_servers_offline = dict()
    resources_map = dict()

    for obj in Contact.objects.all():
      resources_map[obj.urlid] = obj
      if hasattr(obj, "contact"):
        try:
          url = urlparse(obj.contact).netloc
          if(url not in ignored):
            try:
              contact = get_user_model().objects.get(urlid=obj.contact)
              if(contact.urlid):
                if(not contact.urlid.startswith(settings.BASE_URL)):
                  url = urlparse(contact.urlid).netloc
                  if(url not in ignored):
                    try:
                      if(is_alive(obj.urlid, 404)):
                        resources_404.add(obj.urlid)
                    except:
                      resources_servers_offline.add(obj.urlid)
            except:
              resources_404.add(obj.urlid)
        except:
          resources_404.add(obj.urlid)


    if(len(resources_404) > 0):
      print("Faulted contacts, 404:")
      for resource in resources_404:
        print("- "+resource)
      if(options["fix_404_resources"]):
        for resource in resources_404:
          try:
            resources_map[resource].delete()
          except:
            pass
        print("Fixed 404 contacts")
      else:
        print("Fix them with `./manage.py check_integrity --fix-404-resources`")

    if(len(resources_servers_offline) > 0):
      print("Faulted contacts, servers offline:")
      for resource in resources_servers_offline:
        print("- "+resource)
      if(options["fix_offline_servers"]):
        for resource in resources_servers_offline:
          try:
            resources_map[resource].delete()
          except:
            pass
        print("Fixed contacts on offline servers")
      else:
        print("Fix them with `./manage.py check_integrity --fix-offline-servers`")

    if(len(resources_servers_offline) == 0 and len(resources_404) == 0):
      print('Everything goes fine')

  else:
    print("Ignoring djangoldp-contact checks")