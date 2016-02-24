#!/usr/bin/env python
from github import Github
from os.path import expanduser , exists
from optparse import OptionParser
#from process_pr import process_pr
from github_hooks_config import GITHUB_HOOKS as hk_conf
from github_hooks_config import REPO_HOOK_MAP
import hashlib, re
from categories import EXTERNAL_REPOS, CMSSW_REPOS, CMSDIST_REPOS
from sys import exit

#Get secret from file
def get_secret(hook_name):
  secret_file = '/data/secrets/' + hook_name
  if not exists(secret_file):
    secret_file = '/data/secrets/github_hook_secret_cmsbot' 
  return open(secret_file,'r').read().split('\n')[0].strip()
#match hook config
def match_config(new,old):
  if new["active"] != old.active:
    return False
  elif new["events"] != old.events:
    return False
  for key in new["config"]:
    if (not key in old.config) or (key!='secret' and new["config"][key] != old.config[key]):
      return False
  return True
  
#main section
if __name__ == "__main__":
  parser = OptionParser(usage="%prog [-k|--hook <name>] [-r|--repository <repo>] [-f|--force] [-n|--dry-run]")
  parser.add_option("-n", "--dry-run",   dest="dryRun",     action="store_true", help="Do not modify Github", default=False)
  parser.add_option("-f", "--force",     dest="force",     action="store_true", help="Force update github hook", default=False)
  parser.add_option("-r", "--repository",dest="repository", help="Github Repositoy name e.g. cms-sw/cmssw.", type=str, default=None)
  parser.add_option("-e", "--externals", dest="externals", action="store_true", help="Only process CMS externals repositories", default=False)
  parser.add_option("-c", "--cmssw",     dest="cmssw",     action="store_true", help="Only process "+",".join(CMSSW_REPOS)+" repository", default=False)
  parser.add_option("-d", "--cmsdist",   dest="cmsdist",   action="store_true", help="Only process "+",".join(CMSDIST_REPOS)+" repository", default=False)
  parser.add_option("-a", "--all",       dest="all",       action="store_true", help="Process all CMS repository i.e. externals, cmsdist and cmssw", default=False)
  parser.add_option("-k", "--hook", dest="hook", help="Github Hook name", type=str, default="")
  opts, args = parser.parse_args()

  repos_names = []
  if opts.repository:
    repos_names.append(opts.repository)
  elif opts.all:
    opts.externals = True
    opts.cmssw = True
    opts.cmsdist = True
  elif (not opts.externals) and (not opts.cmssw) and (not opts.cmsdist):
    parser.error("Too few arguments, please use either -e, -c or -d")

  if not repos_names:
    if opts.externals: repos_names = repos_names + EXTERNAL_REPOS
    if opts.cmssw: repos_names = repos_names + CMSSW_REPOS
    if opts.cmsdist: repos_names = repos_names + CMSDIST_REPOS

  gh = Github(login_or_token = open(expanduser("~/.github-token")).read().strip())
  #get repos to be processed
  repos = {}
  for r in set(repos_names):
    if not "/" in r:
      for repo in gh.get_user(r).get_repos():
        repos[repo.full_name]=repo
    else:
      repos[r]=None

  #process repos
  error = 0
  for repo_name in repos:
    print "Checking for repo ",repo_name
    hooks = []
    for r in REPO_HOOK_MAP:
      if re.match(r[0],repo_name):
        if opts.hook and opts.hook in r[1]:
          hooks.append(opts.hook)
          break
        elif not opts.hook:
          for h in r[1]: hooks.append(h)
        break
    if not hooks:
      print "==>Warning: No hook found for repository",repo_name
      error = 1
      continue

    err = 0
    for h in hooks:
      if not h in hk_conf:
        print "==>Error: No hook name ",h," found for repository ",repo_name
        err = 1
    if err:
      error = 1
      continue

    print "Found hooks:",hooks
    repo = repos[repo_name]
    if not repo: repo = gh.get_repo(repo_name)
    repo_hooks_all = {}
    for hook in repo.get_hooks():
      if "name" in hook.config:
        repo_hooks_all[ hook.config['name'] ] = hook 

    for hook in hooks:
      print "checking for web hook" , hook
      hook_conf = hk_conf[hook]
      hook_conf["name"] = "web"
      hook_conf["config"]["insecure_ssl"] = "1"
      hook_conf["config"]["secret"] = get_secret(hook)
      hook_conf["config"]["name"] = hook
      hook_conf["config"]["data"] = hashlib.sha256(hook_conf["config"]["secret"].encode()).hexdigest()
      if hook in repo_hooks_all:
        old_hook = repo_hooks_all[hook]
        if opts.force or not match_config(hook_conf,old_hook):
          if not opts.dryRun: old_hook.edit(**hook_conf)
          print "hook updated"
        else:
          print "Hook configuration is same"
      else:
        if not opts.dryRun: repo.create_hook(**hook_conf)
        print "Hook created in github.....success"
  exit(error)
