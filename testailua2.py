#########################################
# Niilo Liimatainen
# 29.03.2021
# Sources:
# https://www.mediawiki.org/wiki/API:Links
# https://github.com/stong1108/WikiRacer/blob/master/wikiracer_threaded.py
# https://github.com/rklabs/WikiRacer/blob/master/wikiracer.py
# https://www.geeksforgeeks.org/python-set-difference/
#########################################
import requests
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed
from multiprocessing import Manager
import traceback
import time
import re
import threading

URL = "https://en.wikipedia.org/w/api.php"


# The function will return all the hyperlinks that are in the given Wikipedia page
# This function is made from the Wikipedia API documentation's example
def get_links(node):
	try:
		
		counter = 0
		titles = 0
		title_filter = "Category:|Template:|Template talk:|Wikipedia:|Book:|Portal:|Help:|File:|MediaWiki:|MediaWiki talk|User talk:|Wikipedia talk:|Draft:|User:|Talk:|Module:"
		link_list = []
		session = requests.Session()
		PARAMS = {
			"action": "query",
			"titles": node,
			"prop": "links",
			"pllimit": "max",
			"format": "json",
			"pldir": "descending"
		}

		response = session.get(url=URL, params=PARAMS)
		data = response.json()
		pages = data["query"]["pages"]

		for key, value in pages.items():
			for link in value["links"]:
				counter += 1
				if not re.search(title_filter, link["title"]):
					titles += 1
					link_list.append(link["title"])
		
		while "continue" in data:
			PARAMS["plcontinue"] = data["continue"]["plcontinue"]
			response = session.get(url=URL, params=PARAMS)
			data = response.json()
			pages = data["query"]["pages"]

			for key, value in pages.items():
				for link in value["links"]:
					counter += 1
					if not re.search(title_filter, link["title"]):
						titles += 1
						link_list.append(link["title"])	
		return link_list
	except Exception:
		traceback.print_exc()
		return []


# Function to fetch all the links for each node in parallel
def fetch_links(path, links_dict):
	# Creating a threadpool with own worker for each node
	with ThreadPoolExecutor(max_workers=len(path)) as executor:
		futures = {}

		for node in path:
			# If node's links aren't found yet, then get the links
			if not links_dict.get(node):
				futures[executor.submit(get_links, node)] = node
		
		# Looping through futures and taking the result when future is completed
		for future in as_completed(futures):
			try:
				links_dict[futures[future]] = future.result()
			except Exception:
				links_dict[node] = []



# Function to validate if start and end pages are valid
def page_validation(title):
	try:
		response = requests.get("https://en.wikipedia.org/wiki/" + title)
		if response.status_code == 404:
			return 0
		return 1
	except:
		print("Exception happened in request!")



def find_shortest_path(page, end_page, path, shortest_path):
	if page.lower() == end_page.lower():
		new_path = path + [page]
		shortest_path[len(new_path)] = new_path
		return True
	else:
		return False


def breadth_first_search(start_page, end_page):
	# Testing that start and end pages are valid
	if not page_validation(start_page) or not page_validation (end_page):
		return "Invalid start or end page!"

	# Path and link dictionaries for nodes
	shortest_path = Manager().dict()
	links_dict = Manager().dict()

	# Queue with tuple that holds page title and path to it
	queue = [(start_page, [start_page])]
	visited = []

	while queue:
		# Removing the first tuple in queue
		node, path = queue.pop(0)
		fetch_links(path, links_dict)
		# Loop through all the nodes in path except the destination
		for n in path:
			if n not in visited:
				links = links_dict[n]
				visited.append(n)
				if end_page in links:
					for page in links:
						if page == end_page:
							new_path = path + [page]
							shortest_path[len(new_path)] = new_path
							return shortest_path	
				for page in links:
					queue.append((page, path + [page]))
	return shortest_path
					

def main():
	start = time.time()
	start_page = "Finland"
	end_page = "Computer"
	shortest_path = breadth_first_search(start_page, end_page)
	end = time.time()
	run_time = (end - start) / 60
	print(shortest_path)
	print(f"Runtime of the algorithm was {round(run_time, 2)} minutes!")



				

if __name__ == "__main__":
	main()


"""
with ProcessPoolExecutor(max_workers=6) as executor:
					futures = []
					for page in links:
						print(page)
						futures.append(executor.submit(find_shortest_path, page, end_page, path, shortest_path))
					
					for future in as_completed(futures):
						found = future.result()
						if found:
							return shortest_path
						counter += 1
						queue.append((page, path + [page]))
"""

"""
for page in links:
					found = find_shortest_path(page, end_page, path, shortest_path)		
					if not found:
						queue.append((page, path + [page]))
					else:
						return shortest_path
"""