from django.conf import settings
from django.contrib.auth import get_user_model
from djangoldp_project.models import Member
from djangoldp.check_integrity import is_alive
from urllib.parse import urlparse

def add_arguments(parser):
  parser.add_argument(
    "--ignore-project-members",
    default=False,
    nargs="?",
    const=True,
    help="Ignore project members related check",
  )

def check_integrity(options):
  print('---')
  print("DjangoLDP Project")
  if(not options["ignore_project_members"]):

    ignored = set()
    if(options["ignore"]):
      for target in options["ignore"].split(","):
        ignored.add(urlparse(target).netloc)

    resources_404 = set()
    resources_servers_offline = set()
    resources_map = dict()

    for obj in Member.objects.all():
      resources_map[obj.urlid] = obj
      if hasattr(obj, "user"):
        if(obj.user.urlid):
          if(not obj.user.urlid.startswith(settings.BASE_URL)):
            url = urlparse(obj.user.urlid).netloc
            if(url not in ignored):
              try:
                if(is_alive(obj.user.urlid, 404)):
                  resources_404.add(obj.urlid)
              except:
                resources_servers_offline.add(obj.urlid)
        else:
          resources_404.add(obj.urlid)
      if hasattr(obj, "project"):
        if(obj.project.urlid):
          if(not obj.project.urlid.startswith(settings.BASE_URL)):
            url = urlparse(obj.project.urlid).netloc
            if(url not in ignored):
              try:
                if(is_alive(obj.project.urlid, 404)):
                  resources_404.add(obj.urlid)
              except:
                resources_servers_offline.add(obj.urlid)
        else:
          resources_404.add(obj.urlid)

    if(len(resources_404) > 0):
      print("Faulted project memberships, 404:")
      for resource in resources_404:
        print("- "+resource)
      if(options["fix_404_resources"]):
        for resource in resources_404:
          try:
            resources_map[resource].delete()
          except:
            pass
        print("Fixed 404 project memberships")
      else:
        print("Fix them with `./manage.py check_integrity --fix-404-resources`")

    if(len(resources_servers_offline) > 0):
      print("Faulted project memberships, servers offline:")
      for resource in resources_servers_offline:
        print("- "+resource)
      if(options["fix_offline_servers"]):
        for resource in resources_servers_offline:
          try:
            resources_map[resource].delete()
          except:
            pass
        print("Fixed project memberships on offline servers")
      else:
        print("Fix them with `./manage.py check_integrity --fix-offline-servers`")

    if(len(resources_servers_offline) == 0 and len(resources_404) == 0):
      print('Everything goes fine')

  else:
    print("Ignoring djangoldp-project checks")