from typing import Any
import os
import socket
import traceback
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
import json
import re
from datetime import datetime
from scrapy.http import HtmlResponse
from concurrent.futures import ThreadPoolExecutor
import requests
import hashlib
import time
import unicodedata
import pymongo
import pandas as pd
from pymongo.errors import PyMongoError
from openpyxl import Workbook
import csv
import html
import math
import mimetypes
from bs4 import BeautifulSoup
import sys
from .configuration import *
try:
    sys.path.insert(0,tracetuneel_path)
    import request_engine
except:
    pass

try:
    mongo_client = MongoClient(connection_string)
    db = mongo_client[data_base]
    col_input = db[input_table]
    col_input_pdp = db[pl_input_table]
    log = db[f'failures_collection']
    print("✅ MongoDB connection successful")
except Exception as e:
    print(e)




def get_lan_ipv4():
    hostname = socket.gethostname()
    # Get all addresses associated with the hostname
    addresses = socket.gethostbyname_ex(hostname)[2]

    for ip in addresses:
        # Check for private IPv4 ranges
        if ip.startswith("192.") or ip.startswith("10.") or ip.startswith("172."):
            return ip
    return None





def clean_data(doc):
    CLEANR = re.compile(r'<.*?>|&([a-z0-9]+|#x[0-9]{1,6}|#x[0-9a-f]{1,6});|[\t\n\r]')
    def text_cleaner(text: str) -> str:
        decodehtml = html.unescape(text.encode('utf-8', 'ignore').decode("utf-8"))
        htmltagremove = re.sub(CLEANR, '', decodehtml)
        escaperemove = re.sub(r'\s+', ' ', htmltagremove)
        return unicodedata.normalize('NFKD', escaperemove.strip()).encode('utf_8_sig', 'ignore').decode("utf_8_sig")

    def clean_string(text: str) -> str:
        if not text:
            return ""

        if isinstance(text, str):
            # Normalize common HTML entities and unwanted chars via regex
            replacements = {
                r"&gt;": ">",
                r"&lt;": "<",
                r"&amp;": "&",
                r"&nbsp;": " ",
                r"": "",        # odd char cleanup
                r"[\r\n\t]+": " "  # whitespace control
            }
            for pat, repl in replacements.items():
                text = re.sub(pat, repl, text, flags=re.IGNORECASE)

            # Remove scripts, styles, comments, tags
            text = re.sub(r"<script[^>]*>[\w\W]*?</script>", " ", text, flags=re.IGNORECASE)
            text = re.sub(r"\* style specs start[^>]*>[\w\W]*?style specs end *", " ", text, flags=re.IGNORECASE)
            text = re.sub(r"<style[^>]*>[\w\W]*?</style>", " ", text, flags=re.IGNORECASE)
            text = re.sub(r"<!--[\w\W]*?-->", " ", text, flags=re.IGNORECASE)
            text = re.sub(r"<[^>]+>", " ", text)   # all tags
            text = re.sub(r"\s+", " ", text)       # collapse multiple spaces

            return text_cleaner(text).strip()

        return str(text)

    cleaned = {}
    for k, v in doc.items():
        key = k.strip() if isinstance(k, str) else k

        if isinstance(v, str):
            v = clean_string(v)

        elif isinstance(v, list):
            v = [clean_string(item) for item in v if isinstance(item, str) and item.strip()]

        cleaned[key] = v

    return cleaned


def doc_hash(doc):
    return hashlib.md5(json.dumps(doc, sort_keys=True).encode()).hexdigest()

def is_valid_page_save(doc, parcel_number):
    if not parcel_number:
        return "missing parcel_number"

    page_save = doc.get("page_save")

    if page_save.startswith("\\\\") or re.match(r"^[A-Za-z]:\\", page_save) or "\\" in page_save:
        return "invalid_path"

    if not isinstance(page_save, str) or not page_save.strip():
        return "empty"

    check_page_save = page_save.replace(".html", "").replace(".json", "")
    if str(parcel_number) in check_page_save:
        return "valid"
    else:
        return "does not match parcel_number"

def InsertItem(data=None,retry=None,parcel_number=None,table_name=None):
    if not data:
        print({"status": "error", "message": "InsertItem: No data provided."})
        return
    try:
        retry=str(retry)
    except:
        retry=retry
    if retry and parcel_number and table_name:
        try:
            Checking_pagesave = is_valid_page_save(data, parcel_number)
            if isinstance(data, dict):
                if Checking_pagesave == "empty":
                    print("InsertItem: 'page_save' is missing or Wrong Key. Skipping.")
                    return
                elif Checking_pagesave == "does not match parcel_number":
                    print(f"[ERROR] page_save does not match parcel_number '{parcel_number}' or has an invalid extension")
                    return
                elif Checking_pagesave == "missing parcel_number":
                    print("[ERROR] parcel_number is missing")
                    return
                elif Checking_pagesave=="invalid_path":
                    print("page_save contains an invalid file path (UNC or drive letter not allowed)")
                    return
                elif Checking_pagesave == "valid":
                    data = clean_data(data)
                    if table_name:
                        data['_id'] = doc_hash(data)
                        try:
                            now = datetime.now()
                            formatted = now.strftime("%Y-%m-%d %H:%M:%S")
                            data['datetime']=formatted
                            data['retry'] = retry
                            lan_ip = get_lan_ipv4()
                            data['IP']=lan_ip
                        except:
                            pass
                        db[table_name].insert_one(data)
                        print("✅ Successfully inserted document")
                else:
                    print(f"Unrecognized status Please check logic or data.")
            else:
                print("InsertItem: Data is not a dictionary. Skipping.")
        except DuplicateKeyError as e:
            print("Duplicate key error: Document already exists.")
    elif retry is None or parcel_number is None:
        print({"status": "error", "message": "Missing required parameters: 'retry' or 'parcel_number' or 'table_name'"})

MAX_RETRIES = 3
RETRY_DELAY = 2
def fetch_response(method="GET",url=None,headers=None,data=None, params=None,cookies=None,proxy=None,feedid="",parcel_number=None,proxy_region=None,verify=None,session=None,timeout=None,pagesave_path=pagesave_path,allow_redirects=None,document_request=None,verify_text=None):
    retries = 0
    if parcel_number and len(parcel_number) >= 4 and url:
        parcel_id = str(parcel_number)
        if not re.match(r'^[A-Za-z0-9_\- .]+$', parcel_id):
            return (f"[INVALID] parcel_number '{parcel_id}' contains junk characters.", "0")

        try:
            if not os.path.exists(pagesave_path):
                os.makedirs(pagesave_path)
        except Exception as e:
            return (e,"0")

        try:
            file_path = os.path.join(pagesave_path, f"{parcel_number}.html")
            if os.path.exists(file_path):
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    cached = f.read()
                    print(f"Page Read HTML file for parcel_number '{parcel_number}'.")
                return (HtmlResponse(url=url, body=cached, encoding='utf-8'), retries)
        except Exception as e:
            return (None,e)

        try:
            file_path = os.path.join(pagesave_path, f"{parcel_number}.json")
            if os.path.exists(file_path):
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    cached = f.read()
                return (HtmlResponse(url=url, body=cached, encoding='utf-8'), retries)
        except Exception as e:
            return (None,e)

        if proxy is None or  isinstance(proxy, dict) and "http" in proxy and "https" in proxy:

            while retries <= MAX_RETRIES:
                try:
                    request_args = {
                        "method": method,
                        "url": url
                    }
                    if headers:
                        request_args["headers"] = headers
                    if data:
                        request_args["data"] = data
                    if params:
                        request_args["params"] = params
                    if cookies:
                        request_args["cookies"] = cookies
                    if verify is not None:
                        request_args["verify"] = verify
                    if proxy is not None:
                        request_args["proxies"] = proxy
                    if timeout is not None:
                        request_args["timeout"] = timeout
                    if allow_redirects is not None:
                        request_args["allow_redirects"] = allow_redirects

                    if session is True:
                        sess = requests.Session()
                        r = sess.request(**request_args)
                        retries += 1
                    if session is None:
                        r = requests.request(**request_args)
                        retries += 1
                    if r.status_code == 200:
                        if document_request is True:
                            try:
                                content_type = r.headers.get("Content-Type", "").lower()
                                file_size = len(r.content)
                                if document_request and file_size < 1000:
                                    print(f"⚠️ File too small ({file_size} bytes), likely error page.")
                                    return (r, retries)
                                if document_request and ("text/html" in content_type or "text/plain" in content_type):
                                    return (r, retries)
                                ext = mimetypes.guess_extension(content_type.split(";")[0]) or ".bin"
                                file_path = os.path.join(pagesave_path, f"{parcel_number}{ext}")
                                if os.path.exists(file_path):
                                    print(f"📄 Document already saved, using cache → {file_path}")
                                    return (r, retries)
                                elif not os.path.exists(file_path):
                                    with open(file_path, "wb") as f:
                                        f.write(r.content)
                                    print(f"📄 Document saved: {file_path}")
                                    return (r, retries)
                            except Exception as e:
                                return (e,retries)
                        if document_request is None:
                            try:
                                is_json = False
                                try:
                                    json_data = r.json()
                                    is_json = True
                                except ValueError:
                                    pass
                                if verify_text:
                                    if verify_text in r.text:
                                        file_path = os.path.join(pagesave_path, f"{parcel_number}.html")
                                        with open(file_path, "w", encoding="utf-8", errors="ignore") as f:
                                            f.write(r.text)

                                    else:
                                        return ("Text verification failed", "0")

                                elif verify_text is None or verify_text=='':
                                    if is_json:
                                        file_path = os.path.join(pagesave_path, f"{parcel_number}.json")
                                        with open(file_path, "w", encoding="utf-8") as f:
                                            json.dump(json_data, f, ensure_ascii=False, indent=4)
                                    else:
                                        file_path = os.path.join(pagesave_path, f"{parcel_number}.html")
                                        with open(file_path, "w", encoding="utf-8", errors="ignore") as f:
                                            f.write(r.text)
                            except Exception as e:
                                return (e,retries)

                        file_size = os.path.getsize(file_path)
                        if file_size < 50:
                            print(f"Warning: {file_path} is too small, possible error page.")
                        if file_size>50:
                            r=HtmlResponse(url=r.url, body=r.text, encoding='utf-8')
                            return (r, retries)
                    else:
                        retries += 1
                        time.sleep(RETRY_DELAY)
                except requests.exceptions.RequestException as e:
                    print(f"Issue Connection reset for parcel_number: {parcel_number}",e)
                    retries += 1
                    time.sleep(RETRY_DELAY)

            else:
                log.insert_one({
                    "parcel_number": parcel_number,
                    "URL": url,
                    "Retries": retries,
                    "Trace": traceback.format_exc(),
                    "Logged_At": datetime.now()
                })
                try:
                    if r.status_code:
                        return (r, retries)
                    else:
                        return (None, retries)
                except:
                    pass

        if proxy:
            while retries <= MAX_RETRIES:
                try:
                    args = {
                        "url": url,
                        "headers": headers,
                        "request_type": method,
                        "proxy": proxy,
                        "payload": data,
                        "proxy_region": proxy_region,
                        "projectid": "3421",
                        "feedid": feedid,
                        "cookies": cookies,
                    }
                    response = request_engine.make_xbt_request(**args)
                    retries += 1
                    if response.status_code == 200:
                        try:
                            try:
                                json_data = response.json()
                                is_json = True
                            except ValueError:
                                is_json = False

                            if is_json:
                                file_path = os.path.join(pagesave_path, f"{parcel_number}.json")
                                with open(file_path, "w", encoding="utf-8") as f:
                                    json.dump(json_data, f, ensure_ascii=False, indent=4)
                            else:
                                file_path = os.path.join(pagesave_path, f"{parcel_number}.html")
                                with open(file_path, "w", encoding="utf-8", errors="ignore") as f:
                                    f.write(response.text)
                        except Exception as e:
                            return (e,retries)

                        file_size = os.path.getsize(file_path)
                        if file_size < 50:
                            print(f"Warning: {file_path} is too small, possible error page.")
                            return (response, retries)
                        if file_size > 50:
                            response = HtmlResponse(url=response.url, body=response.text, encoding='utf-8')
                            return (response, retries)
                    else:
                        retries += 1
                        time.sleep(RETRY_DELAY)
                except requests.exceptions.RequestException as e:
                    print(f"Issue Connection reset for parcel_number: {parcel_number}",e)
                    retries += 1
                    time.sleep(RETRY_DELAY)
            else:
                log.insert_one({
                    "parcel_number": parcel_number,
                    "URL": url,
                    "Retries": retries,
                    "Trace": traceback.format_exc(),
                    "Logged_At": datetime.now()
                })

                try:
                    if response.status_code:
                        return (response, retries)
                    else:
                        return (None, retries)
                except:
                    pass
    elif parcel_number is None:
        return ("Please pass a parcel_number in request",None)
    elif len(parcel_number)<=4:
        return ("parcel_number is wrong", None)
    elif url is None:
        return ("error: url not provided", None)



def update_input(key,value,status):
    try:
        col_input.update_one({f'{key}': value}, {'$set': {f'status': f"{status}"}})
    except Exception as e:
        print(e)

def update_input_many(key,value,status):
    try:
        col_input.update_many({f'{key}': value}, {'$set': {f'status': f"{status}"}})
    except Exception as e:
        print(e)

def update_pl_input(key,value,status):
    try:
        col_input_pdp.update_one({f'{key}': value}, {'$set': {f'status': f"{status}"}})
    except Exception as e:
        print(e)

def update_pl_input_many(key,value,status):
    try:
        col_input_pdp.update_many({f'{key}': value}, {'$set': {f'status': f"{status}"}})
    except Exception as e:
        print(e)

def get_input(query=None,limit=None,skip=0):
    try:
        if query is None:
            data=col_input.find({})
        if query:
            data = col_input.find(query)
        if limit is not None:
            limit = int(limit)
            data = col_input.find(query).skip(int(skip)).limit(int(limit))
        return data
    except:
        return None

def pl_input(query=None,limit=None,skip=0):
    try:
        if query is None:
            data1=col_input_pdp.find({})
        if query:
            data1 = col_input_pdp.find(query)
        if limit is not None:
            limit = int(limit)
            data1 = col_input_pdp.find(query).skip(int(skip)).limit(int(limit))
        return data1
    except:
        return None


def export_mongo_to_csv(filename=None, collectionname=None, directory=None):
    if filename and collectionname:
        try:
            if not os.path.exists(directory):
                os.makedirs(directory)
        except Exception as e:
            print({"status": "error", "message": "Folder not created"})
            return

        now = datetime.now()
        formatted = now.strftime("%Y-%m-%d %H:%M:%S")
        print(f"📂 Export process started at: {formatted}")
        documents = list(db[collectionname].find({}))
        if not documents:
            print("No data found in collection.")
            return

        exclude_fields = {"_id", "retry", "datetime"}
        field_order = []
        seen = set()

        # Collect all unique keys except excluded ones
        for doc in documents:
            for key in doc.keys():
                key_lower = key.lower()
                if key not in exclude_fields and key_lower not in seen:
                    field_order.append(key_lower)
                    seen.add(key_lower)

        # Ensure page_save is last if it exists
        if "page_save" in field_order:
            field_order.remove("page_save")
            field_order.append("page_save")

        filepath = os.path.join(directory, f"{filename}.csv")
        with open(filepath, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=field_order)
            writer.writeheader()
            for doc in documents:
                cleaned_doc = {
                    k.lower(): re.sub(r'\s{2,}', ' ', str(v)).strip()
                    for k, v in doc.items()
                    if k not in exclude_fields
                }
                row = {key: cleaned_doc.get(key, "") for key in field_order}
                writer.writerow(row)

        print(f"✅ Export Successful! {filepath}")
        print(f"📂 Export process end at: {formatted}")
    else:
        print({"status": "error","message": "Missing filename and collectionname. Please provide filename, collectionname"})


def export_mongo_to_excel(filename=None, collectionname=None, directory=None, skip=0, limit=0):
    if filename and collectionname:
        try:
            if not os.path.exists(directory):
                os.makedirs(directory)
        except Exception as e:
            print({"status": "error", "message": "Folder not created"})
            return

        now = datetime.now()
        formatted_start = now.strftime("%Y-%m-%d %H:%M:%S")
        print(f"📂 Export process started at: {formatted_start}")

        # Apply skip and limit
        cursor = db[collectionname].find({})
        if skip:
            cursor = cursor.skip(skip)
        if limit:
            cursor = cursor.limit(limit)

        documents = list(cursor)
        if not documents:
            print("No data found in collection.")
            return

        exclude_fields = {"_id", "retry", "datetime"}
        field_order = []
        seen = set()

        # Collect all unique keys except excluded ones
        for doc in documents:
            for key in doc.keys():
                key_lower = key.lower()
                if key not in exclude_fields and key_lower not in seen:
                    field_order.append(key_lower)
                    seen.add(key_lower)

        # Ensure page_save is last if it exists
        if "page_save" in field_order:
            field_order.remove("page_save")
            field_order.append("page_save")

        # Create Excel workbook
        wb = Workbook()
        ws = wb.active
        ws.title = collectionname

        # Write headers
        ws.append(field_order)

        # Write rows
        for doc in documents:
            cleaned_doc = {
                k.lower(): re.sub(r'\s{2,}', ' ', str(v)).strip()
                for k, v in doc.items()
                if k not in exclude_fields
            }
            row = [cleaned_doc.get(key, "") for key in field_order]
            ws.append(row)

        filepath = os.path.join(directory, f"{filename}.xlsx")
        wb.save(filepath)

        now_end = datetime.now()
        formatted_end = now_end.strftime("%Y-%m-%d %H:%M:%S")
        print(f"✅ Export Successful! {filepath}")
        print(f"📂 Export process end at: {formatted_end}")
    else:
        print({"status": "error","message": "Missing filename and collectionname. Please provide filename, collectionname"})








def extract_all_key_values(html_content):
    soup = BeautifulSoup(html_content, "html.parser")
    data = {}
    def clean_text(text):
        """Normalize whitespace and preserve special chars."""
        if not text:
            return ""
        text = text.replace("\xa0", " ").replace("\n", " ").strip()
        text = re.sub(r"\s+", " ", text)
        return text

    # 1️⃣ <p>Key:</p><p>Value</p>
    for container in soup.find_all("div"):
        p_tags = container.find_all("p", recursive=False)
        for i in range(len(p_tags) - 1):
            key = clean_text(p_tags[i].get_text())
            val_tag = p_tags[i + 1]
            val = clean_text(" ".join(val_tag.stripped_strings))
            if key.endswith(":") and val:
                key = key.rstrip(":").strip()
                if key not in data:
                    data[key] = val

    # 2️⃣ Current Values / React sc-cPuPxo / sc-FQuPU layouts
    for block in soup.find_all("div", class_=lambda c: c and ("sc-iHhHRJ" in c or "sc-FQuPU" in c)):
        for sub in block.find_all("div", class_=lambda c: c and ("sc-cPuPxo" in c or "sc-FQuPU" in c)):
            p_tags = sub.find_all("p", recursive=False)
            if len(p_tags) >= 2:
                key = clean_text(p_tags[0].get_text())
                val = clean_text(" ".join(p_tags[1].stripped_strings))
                if key and val and key not in data:
                    data[key] = val

    # 3️⃣ <dl><dt><dd>
    for dl in soup.find_all("dl"):
        for dt in dl.find_all("dt"):
            key = clean_text(dt.get_text())
            dd = dt.find_next_sibling("dd")
            val = clean_text(dd.get_text()) if dd else ""
            if key and val and key not in data:
                data[key] = val

    # 4️⃣ div.form-group layout
    for row in soup.find_all("div", class_=lambda c: c and "form-group" in c):
        labels = row.find_all("label")
        divs = row.find_all("div", recursive=False)
        for idx, label in enumerate(labels):
            key = clean_text(label.get_text()).rstrip(":")
            if idx < len(divs):
                val = clean_text(divs[idx].get_text())
                if key and val and key not in data:
                    data[key] = val

    # 5️⃣ <table> key-value pairs
    for table in soup.find_all("table"):
        for row in table.find_all("tr"):
            cells = row.find_all(["td", "th"])
            # Process pairs (0→1, 2→3, etc.)
            for i in range(0, len(cells) - 1, 2):
                key = clean_text(cells[i].get_text()).rstrip(":")
                val = clean_text(cells[i + 1].get_text())
                if (
                        key
                        and val
                        and len(key) < 100
                        and len(val) < 400
                        and key not in data
                        and not re.search(r"Legal Description", key, flags=re.I)
                ):
                    data[key] = val

    # 6️⃣ <li><strong>Key</strong> Value
    for li in soup.find_all("li"):
        strong = li.find("strong")
        if strong:
            key = clean_text(strong.get_text()).rstrip(":")
            strong.extract()
            val = clean_text(li.get_text())
            if key and val and key not in data:
                data[key] = val

    # 7️⃣ <b>Key:</b> Value <br>
    for div in soup.find_all("div", class_=lambda c: c and "detailsCol" in c):
        for b_tag in div.find_all("b"):
            key = clean_text(b_tag.get_text()).rstrip(":")
            val_parts = []
            for sibling in b_tag.next_siblings:
                if getattr(sibling, "name", None) == "br":
                    break
                if isinstance(sibling, str):
                    val_parts.append(sibling)
                else:
                    val_parts.append(sibling.get_text())
            val = clean_text(" ".join(val_parts))
            if key and val and key not in data:
                data[key] = val

    # 8️⃣ Assessor <span class="asr-lbl">Key:</span> Value
    for assessor in soup.find_all("div", class_="row assessor"):
        for span in assessor.find_all("span", class_="asr-lbl"):
            key = clean_text(span.get_text()).rstrip(":")
            val = ""
            strong = span.find_next_sibling("strong")
            if strong:
                val = clean_text(strong.get_text())
            else:
                next_text = span.next_sibling
                if next_text:
                    val = clean_text(next_text)
            if key and val and key not in data:
                data[key] = val

    # 9️⃣ Multi-column label/value
    for multi in soup.find_all("div", class_="multi-column"):
        for row in multi.find_all("div", class_="row"):
            label_div = row.find("div", class_="column label")
            value_div = row.find("div", class_="column value")
            if label_div and value_div:
                key = clean_text(label_div.get_text())
                val = clean_text(value_div.get_text())
                if key and val and key not in data:
                    data[key] = val

    # 🔟 DevExtreme tables
    for dx_table in soup.find_all("table", class_=lambda c: c and "dx-datagrid-table" in c):
        for row in dx_table.find_all("tr", class_=lambda c: c and "dx-row" in c):
            cells = row.find_all("td")
            if len(cells) >= 3:
                key_cell, val_cell = cells[1], cells[2]
                strong = key_cell.find("strong")
                key = clean_text(strong.get_text()) if strong else clean_text(key_cell.get_text())
                val = clean_text(val_cell.get_text())
                if key and val and key not in data:
                    data[key] = val

    # 11️⃣ inner-label (flex layouts)
    for label_div in soup.find_all("div", class_=lambda c: c and "inner-label" in c):
        key = clean_text(label_div.get_text()).rstrip(":")
        next_div = label_div.find_next_sibling("div")
        if next_div:
            val = " ".join(next_div.stripped_strings)
            val = re.sub(r"Toggle Tax Year Dropdown.*", "", val, flags=re.I)
            val = clean_text(val)
            if key and val and key not in data:
                data[key] = val

    # 12️⃣ sc-FQuPU / sc-cPuPxo universal React pairs
    for block in soup.find_all("div", class_=lambda c: c and ("sc-FQuPU" in c or "sc-cPuPxo" in c)):
        p_tags = block.find_all("p", recursive=False)
        if len(p_tags) >= 2:
            key = clean_text(p_tags[0].get_text())
            val = clean_text(" ".join(p_tags[1].stripped_strings))
            if key and val and key not in data:
                data[key] = val

    for row in soup.find_all("div", class_=lambda c: c and "row" in c):
        cols = row.find_all("div",class_=lambda c: c and ("column" in c or "col-md" in c or "col-sm" in c or "col-lg" in c))
        if len(cols) >= 2:
            key = clean_text(cols[0].get_text()).rstrip(":")
            val = clean_text(cols[1].get_text())
            if key and val and key not in data:
                data[key] = val

    # 13️⃣ Safe colon fallback
    for text in soup.stripped_strings:
        if ":" in text:
            parts = text.split(":", 1)
            if len(parts) == 2:
                key, val = clean_text(parts[0]), clean_text(parts[1])
                if (
                    key
                    and val
                    and key not in data
                    and len(key) < 80
                    and len(val) < 400
                    and not re.search(r"Legal Description", key, flags=re.I)
                ):
                    data[key] = val

    # 14️⃣ <p><strong>Key:</strong> Value</p> inline
    for p in soup.find_all("p"):
        strong = p.find("strong")
        if strong:
            key = clean_text(strong.get_text()).rstrip(":")
            strong.extract()
            val = clean_text(" ".join(p.stripped_strings))
            if key and val and key not in data:
                data[key] = val

    # 15️⃣ NEW: Generic <div class="row"><div class="column">Key</div><div class="column">Value</div></div>
    for row in soup.find_all("div", class_=lambda c: c and "row" in c):
        columns = row.find_all("div", class_=lambda c: c and "column" in c)
        if len(columns) >= 2:
            key = clean_text(columns[0].get_text()).rstrip(":")
            val = clean_text(columns[1].get_text())
            if key and val and key not in data:
                data[key] = val
    return data



def to_snake_case(text):
    """Convert any text to clean snake_case"""
    text = text.strip().lower()
    text = re.sub(r'[^a-z0-9]+', '_', text)  # replace non-alphanumeric with underscore
    text = re.sub(r'_+', '_', text)  # collapse multiple underscores
    text = text.strip('_')  # remove leading/trailing underscores
    return text

def extract_data_table_values(html):
    soup = BeautifulSoup(html, "html.parser")
    all_results = []
    tables = soup.find_all("table")
    if not tables:
        tables = [soup]
    for tbl in tables:
        rows = []
        table_prefix = ""
        header = []
        header_found = False
        potential_prefix = None

        # --- Process <thead> if exists ---
        thead = tbl.find("thead")
        if thead:
            for tr in thead.find_all("tr"):
                # Get all non-empty cells
                cells = [th.get_text(separator=" ", strip=True) for th in tr.find_all(["th", "td"])]
                cells = [c for c in cells if c.strip()]
                if not cells:
                    continue

                # Title row (single cell)
                if len(cells) == 1 and not header_found:
                    potential_prefix = to_snake_case(cells[0])
                    continue

                # Actual header row (multiple columns)
                if len(cells) > 1 and not header_found:
                    header = [to_snake_case(c) for c in cells]
                    if potential_prefix:
                        table_prefix = potential_prefix + "_"
                    header_found = True
                    break  # stop at first valid header row

        # --- Process <tbody> ---
        tbody = tbl.find("tbody")
        if tbody and header:
            for tr in tbody.find_all("tr", recursive=False):
                row_data = []
                cells = tr.find_all(["td", "th"], recursive=False)
                for cell in cells:
                    # Handle <select> if exists
                    select = cell.find("select")
                    if select:
                        selected = select.find("option", selected=True)
                        if not selected:
                            selected = select.find("option")
                        text = selected.get_text(strip=True) if selected else select.get_text(strip=True)
                    else:
                        text = cell.get_text(separator=" ", strip=True).replace("\xa0", " ")
                    row_data.append(text)

                if any(c.strip() for c in row_data):
                    # Fill missing columns
                    while len(row_data) < len(header):
                        row_data.append("")
                    row_dict = {f"{table_prefix}{header[i]}": row_data[i] for i in range(len(header))}
                    rows.append(row_dict)

        # --- If no <thead>, use first row in <tbody> as header ---
        if not header_found and tbody:
            first_row = tbody.find("tr")
            if first_row:
                header_cells = [to_snake_case(td.get_text(separator=" ", strip=True)) for td in first_row.find_all(["td","th"])]
                header = header_cells
                for tr in tbody.find_all("tr")[1:]:
                    row_data = [td.get_text(separator=" ", strip=True).replace("\xa0", " ") for td in tr.find_all(["td","th"])]
                    if any(c.strip() for c in row_data):
                        while len(row_data) < len(header):
                            row_data.append("")
                        row_dict = {f"{table_prefix}{header[i]}": row_data[i] for i in range(len(header))}
                        rows.append(row_dict)

        if rows:
            all_results.append(rows)

    return all_results