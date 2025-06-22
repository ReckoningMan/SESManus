#!/usr/bin/env python3
import json
import builtwith

url = "https://www.partstree.com"
tech = builtwith.builtwith(url)
print("Detected technologies for {}:".format(url))
print(json.dumps(tech, indent=2))
