#!/usr/bin/env python3
import shutil, sys, time, requests
from threading import Thread
from concurrent.futures import ThreadPoolExecutor

def download(url_list, max_workers=5):
    columns = shutil.get_terminal_size().columns
    result_obj = {}
    running = True

    def echo_progress():
        while running:
            echo_obj = []
            space_size = 0
            space = ""

            for i in result_obj:
                if result_obj[i] is None:
                    echo_obj.append("{}".format(i))
                elif result_obj[i] != 100:
                    echo_obj.append("{} : {}%".format(i, str(result_obj[i])))
                
                space_size = int(columns) - len("Downloading: {}".format(' '.join(echo_obj))) - 1
                space = " " * space_size

            sys.stdout.write("\rDownloading: {}{}".format(' '.join(echo_obj), space))
            sys.stdout.flush()
        else:
            space = " " * int(columns)
            sys.stdout.write("\r{}".format(space))

    def dl(url):
        file_name = url.split("/")[-1]
        response = requests.get(url, stream=True)
        total_length = response.headers.get('content-length')
        downloaded = 0

        with open(url.split("/")[-1], 'wb') as f:
            if total_length is None:
                result_obj[file_name] = None
                f.write(response.content)
            else:
                for data in response.iter_content(chunk_size=1024):
                    downloaded += len(data)
                    f.write(data)
                    progress = int(100*downloaded/int(total_length))
                    result_obj[file_name] = progress
    
    thread = Thread(target=echo_progress)
    thread.start()
    executor = ThreadPoolExecutor(max_workers=max_workers)
    
    for url in url_list:
        executor.submit(dl, url)
    
    executor.shutdown()
    running = False

#
# Example Start
#

url_list = [
    "https://cdn.kernel.org/pub/linux/kernel/v5.x/linux-5.8.2.tar.xz",
    "https://cdn.kernel.org/pub/linux/kernel/v5.x/linux-5.7.16.tar.xz",
    "https://cdn.kernel.org/pub/linux/kernel/v5.x/linux-5.4.59.tar.xz",
    "https://cdn.kernel.org/pub/linux/kernel/v4.x/linux-4.19.141.tar.xz"
]

download(url_list, 2)

#
# Example End
#
