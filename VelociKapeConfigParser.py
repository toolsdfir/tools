#!/usr/bin/env python3
import sys
import yaml
import requests
from io import StringIO
import csv
import json

# https://github.com/Velocidex/velociraptor/blob/master/artifacts/definitions/Windows/KapeFiles/Targets.yaml
KAPE_TARGETS_URL = "https://raw.githubusercontent.com/Velocidex/velociraptor/master/artifacts/definitions/Windows/KapeFiles/Targets.yaml"

def get_veloci_modules_list(veloci_config_path):
  modules = []
  with open(veloci_config_path, 'r') as veloci_config_file:
    veloci_config = yaml.safe_load(veloci_config_file)
    for item, doc in veloci_config.items():
      if (item == 'autoexec'):
        for listitem in doc.get('argv'):
          strippedarg = listitem.replace(" ", "")
          if ('=Y' in strippedarg):
            strippedarg = listitem.replace("=Y", "")
            modules.append(strippedarg)
  return modules;

def download_kape_targets_yaml():
    r = requests.get(KAPE_TARGETS_URL, allow_redirects=True)
    return yaml.safe_load(r.content)
  
def get_kape_targets_rules(kape_targets_yaml):
  kape_target_default = ''
  kape_rules_default = ''
  for parameter in kape_targets_yaml.get('parameters'):
    if (parameter.get('name') == 'KapeTargets'):
      kape_target_default = parameter.get('default')
    if (parameter.get('name') == 'KapeRules'):
      kape_rules_default = parameter.get('default')
  return (kape_target_default, kape_rules_default)
  
def get_selected_rules(kape_targets):
  selected_rules = []
  reader = csv.reader(kape_targets.split('\n'), delimiter=',')
  for row in reader:
    if (len(row) > 1 and row[0] in modules_list):
      rules = json.loads((row[1]))
      selected_rules = list(set(selected_rules) | set(rules))
  return selected_rules
  
def get_rule_description(kape_rules, selected_rules):
  result = []
  reader = csv.DictReader(kape_rules.split('\n'), delimiter=',')
  for row in reader:
    if (len(row) > 1 and row['Id'].isdigit() and int(row['Id']) in selected_rules):
      result.append(row['Id'] + '\t' + row['Category'] + '\t' + row['Name'] + '\t' + row['Glob'] + '\t' + row['Comment'])
  return result  
  

if __name__ == "__main__":
  if (len(sys.argv) < 2 or not sys.argv[1].endswith('.yaml')):
    print('Usage: VelociKapeConfigParser <path_to_yaml_file>')
    sys.exit()
  modules_list = get_veloci_modules_list(sys.argv[1])
  targets, rules = get_kape_targets_rules(download_kape_targets_yaml())
  selected_rules = get_selected_rules(targets)
  for description in get_rule_description(rules, selected_rules):
    print(description)