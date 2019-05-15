import sys 
import os 
import requests 
import shutil 
from bs4 import BeautifulSoup 

base_dir = os.getcwd()

# print(" Current working directory is {}".format(base_dir))

try:
	site_name = sys.argv[1]
	project_name = sys.argv[2]
except:
	print("Usage:\npython web_cloner.py www.example.com folder_name")
	sys.exit()

project_path = project_name
os.makedirs(project_path,exist_ok=True)

visited_links = []
error_links = []


def save(bs,element,check):
	links = bs.find_all(element)
	for link in links:
		href = link.get("href")
		if href is not None and href not in visited_links:
			if check in href:
				href = link.get("href")
				print("Working with {}".format(href))
				if "//" in href:
					path_s = href.split("/")
					file_name = ""
					for i in range(3,len(path_s)):
						filename = filename + "/"+path_s[i]
				else:
					file_name = href 
				link = site_name + file_name
				try:
					r = requests.get(link)
				except requests.exceptions.ConnectionError:
					error_links.append(link)
					continue 

				if r.status_code != 200:
					error_links.append(link)
					continue

				os.makedirs(os.path.dirname(project_path + file_name.split("?")[0]),exist_ok=True)
				with open(project_path + file_name.split("?")[0],"wb") as f:
					f.write(r.text.encode('utf8'))
					f.close()
				visited_links.append(link)


def save_assets(html_text):
	bs = BeautifulSoup(html_text,"html.parser")
	save(bs=bs,element="link",check=".css")
	save(bs=bs,element="script",check=".js")

	links = bs.find_all("img")
	for link in links:
		href = link.get("src")
		if href is not None and href not in visited_links:
			print("Working with: {}".format(href))
			if "//" in href:
				path_s = href.split("/")
				file_name = ""
				for i in range(3,len(path_s)):
					file_name = file_name + "/" + path_s[i]
			else:
				file_name = href
			link = site_name + file_name
			try:
				r = requests.get(link,stream=True)
			except requests.exceptions.ConnectionError:
				error_links.append(link)
				continue
			if r.status_code != 200:
				error_links.append(link)
				continue
			os.makedirs(os.path.dirname(project_path + file_name.split("?")[0]),exist_ok=True)
			with open(project_path + file_name.split("?")[0],"wb") as f:
				shutil.copyfileobj(r.raw,f)
			visited_links.append(link)


def crawl(link):
	if "http://" not in link and "https://" not in link:
		link = site_name + link

	if site_name in link and link not in visited_links:
		print("Working with: {}".format(link))
		path_s = link.split("/")
		file_name = ""
		for i in range(3,len(path_s)):
			file_name = file_name + "/" + path_s[i]
		if file_name[len(file_name)-1] != "/":
			file_name = file_name + "/"

		try:
			r = requests.get(link)
		except requests.exceptions.ConnectionError:
			print("Connection Error")
			sys.exit(1)

		if r.status_code != 200:
			print("invalid response")
			sys.exit(1)
		print(project_path + file_name + "index.html")
		os.makedirs(os.path.dirname(project_path + file_name.split("?")[0]),exist_ok=True)
		with open(project_path + file_name.split("?")[0] + "index.html","wb") as f:
			text = r.text.replace(site_name,project_name)
			f.write(text.encode('utf8'))
			f.clode()

		visited_links.append(link)
		save_assets(r.text)

		soup = BeautifulSoup(r.text,"html.parser")

		for link in soup.find_all('a'):
			try:
				crawl(link.get("href"))
			except:
				error_links.append(link.get("href"))

crawl(site_name + "/")
print("Lik crawled\n")
for link in visited_links:
	print("---{}\n".format(link))

print("\n\n\nLink error\n")
for link in error_links:
	print("---{}\n".format(link))


