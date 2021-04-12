#########################################
# Niilo Liimatainen
# 29.03.2021
# Sources:
# https://www.mediawiki.org/wiki/API:Links
# https://github.com/stong1108/WikiRacer/blob/master/wikiracer_threaded.py
# https://github.com/rklabs/WikiRacer/blob/master/wikiracer.py
# https://docs.python.org/3/library/re.html
#########################################
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from multiprocessing import Manager
import traceback
import time
import re

URL_API = "https://fi.wikipedia.org/w/api.php"
URL_WIKI = "https://fi.wikipedia.org/wiki/"


# Function to validate if start and end pages are valid Wikipedia pages
def page_validation(title):
	try:
		response = requests.get(URL_WIKI + title)
		if response.status_code == 404:
			return 0
		return 1
	except:
		traceback.print_exc()
		return 0


# The function will return all the hyperlinks that are in the given Wikipedia page (made from the example in Wikipedia API documentation)
def get_links(node):
	try:
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

		response = session.get(url=URL_API, params=PARAMS)
		data = response.json()
		pages = data["query"]["pages"]

		for key, value in pages.items():
			for link in value["links"]:
				if not re.search(title_filter, link["title"]):
					link_list.append(link["title"])
		
		# Checking if there are more links than the max 500 that were given
		while "continue" in data:
			PARAMS["plcontinue"] = data["continue"]["plcontinue"]
			response = session.get(url=URL_API, params=PARAMS)
			data = response.json()
			pages = data["query"]["pages"]

			for key, value in pages.items():
				for link in value["links"]:
					if not re.search(title_filter, link["title"]):
						link_list.append(link["title"])	
		return link_list
	

	# This occurs if there are no links in the page
	except Exception:
		return []


# Function to fetch all the links for each node in parallel
def fetch_links(end_page, path, links, queue, links_dict, shortest_path):
	# Max workers are cpu.count() + 4	
	with ThreadPoolExecutor() as executor:
		futures = {}
		for node in links:
			# If node's links aren't found yet, then get the links
			if not links_dict.get(node):
				futures[executor.submit(get_links, node)] = node
		# Looping through futures and taking the result when future is completed
		for future in as_completed(futures):
			try:
				new_node = futures[future]
				new_links = future.result()
				if find_shortest_path(end_page, new_links, new_node, path, shortest_path):
					return True
				links_dict[new_node] = new_links
				queue.append((new_node, path + [new_node]))
			except Exception:
				links_dict[node] = []
	return False


# Helper function to check if the end page is in the given links
def find_shortest_path(end_page, links, node, path, shortest_path):
	for page in links:
		if page.lower() == end_page.lower():
			new_path = path + [node, page]
			shortest_path[len(new_path)] = new_path
			return True
	return False


# Function that initializes the breadt-first search between two Wikipedia pages
def breadth_first_search(start_page, end_page):
	try:
		# Testing that start and end pages are valid
		if len(start_page) == 0 or len(end_page) == 0:
			return -1
		
		elif not page_validation(start_page) or not page_validation (end_page):
			return -1
			
		# Path and link dictionaries for nodes
		shortest_path = Manager().dict()
		links_dict = Manager().dict()
		queue = Manager().list()

		# Queue with tuple that holds page title and path to it
		queue = [(start_page, [start_page])]
		links = get_links(start_page)
		
		# Test if end page is a direct link from the starting page
		for page in links:
			if page.lower() == end_page.lower():
				shortest_path[2] = [start_page, end_page]
				return shortest_path

		links_dict[start_page] = links
		visited = []

		while queue:
			# Removing the first tuple in queue
			node, path = queue.pop(0)
			# Test if the node is already visiteds
			if node in visited:
				continue
			links = links_dict[node]
			visited.append(node)

			if fetch_links(end_page, path, links, queue, links_dict, shortest_path):
				return shortest_path

		return shortest_path
	except Exception:
		traceback.print_exc()
		return 0
					

# The main function for independent runs 
def main():
	start = time.time()
	start_page = "Jääkiekko"
	end_page = "Lahti"
	shortest_path = breadth_first_search(start_page, end_page)
	end = time.time()
	run_time = end - start
	print(shortest_path)
	print(f"Runtime of the algorithm was {round(run_time, 2)} seconds!")


if __name__ == "__main__":
	main()

