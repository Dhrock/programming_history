from ast import For, If
import json
import os
import sys
import requests
import time
# If you are using a Jupyter Notebook, uncomment the following line.
# %matplotlib inline
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
from PIL import Image
from io import BytesIO

# Azure の Cognitive Service でエンドポイントとライセンスキーを取得
endpoint = "https://daisuke-asuka.cognitiveservices.azure.com/"
subscription_key = "969d1c0ffac746ff867ed5874e7a7d85"

os.environ['COMPUTER_VISION_ENDPOINT'] = endpoint
os.environ['COMPUTER_VISION_SUBSCRIPTION_KEY'] = subscription_key

missing_env = False
# Add your Computer Vision subscription key and endpoint to your environment variables.
if 'COMPUTER_VISION_ENDPOINT' in os.environ:
    endpoint = os.environ['COMPUTER_VISION_ENDPOINT']
else:
    print("From Azure Cognitive Service, retrieve your endpoint and subscription key.")
    print("\nSet the COMPUTER_VISION_ENDPOINT environment variable, such as \"https://westus2.api.cognitive.microsoft.com\".\n")
    missing_env = True

if 'COMPUTER_VISION_SUBSCRIPTION_KEY' in os.environ:
    subscription_key = os.environ['COMPUTER_VISION_SUBSCRIPTION_KEY']
else:
    print("From Azure Cognitive Service, retrieve your endpoint and subscription key.")
    print("\nSet the COMPUTER_VISION_SUBSCRIPTION_KEY environment variable, such as \"1234567890abcdef1234567890abcdef\".\n")
    missing_env = True

if missing_env:
    print("**Restart your shell or IDE for changes to take effect.**")
    sys.exit()

text_recognition_url = endpoint + "/vision/v3.2/read/analyze?language=ja&model-version=latest"

# image_path = "./in_a_1.png"
# image_path = "./in_a.png"
# image_path = "./in_mu_1.png"
# image_path = "./in_amu_1.png"
# image_path = "./in_tegaki.jpeg"
# image_path = "./in_random.png"
# image_path = "./hoge.jpg"
# image_path = "./hoge2.jpeg"
# image_path = "./resize_a_1.png"
# image_path = "./resize_hoge2.png"
image_path = "./diff_hoge.jpg"

# Local File
headers = {'Ocp-Apim-Subscription-Key': subscription_key,
           'Content-Type': 'application/octet-stream'}
with open(image_path, 'rb') as f:
    data = f.read()
response = requests.post(
    text_recognition_url, headers=headers, data=data)


# URL

# Set image_url to the URL of an image that you want to recognize.
# image_url = "https://raw.githubusercontent.com/MicrosoftDocs/azure-docs/master/articles/cognitive-services/Computer-vision/Images/readsample.jpg"
# image_url = "https://www.peacsmind.com/eyecatch/0000843.jpg"

# headers = {'Ocp-Apim-Subscription-Key': subscription_key}
# data = {'url': image_url}
# response = requests.post(
#     text_recognition_url, headers=headers, json=data)
# response.raise_for_status()

# Extracting text requires two API calls: One call to submit the
# image for processing, the other to retrieve the text found in the image.

# Holds the URI used to retrieve the recognized text.
operation_url = response.headers["Operation-Location"]

# The recognized text isn't immediately available, so poll to wait for completion.
analysis = {}
poll = True

while (poll):
    response_final = requests.get(
        response.headers["Operation-Location"], headers=headers)
    analysis = response_final.json()

    print(json.dumps(analysis, indent=4))
    #
    if ("analyzeResult" in analysis):
        lines = analysis['analyzeResult']['readResults'][0]['lines']
        # テキストの表示
        print()
        [print(line['text']) for line in lines]
        print()
    #

    time.sleep(1)
    if ("analyzeResult" in analysis):
        poll = False
    if ("status" in analysis and analysis['status'] == 'failed'):
        poll = False

polygons = []
if ("analyzeResult" in analysis):
    # Extract the recognized text, with bounding boxes.
    polygons = [(line["boundingBox"], line["text"])
                for line in analysis["analyzeResult"]["readResults"][0]["lines"]]

# Display the image and overlay it with the extracted text.
# image = Image.open(BytesIO(requests.get(image_url).content))
image = Image.open(image_path)
ax = plt.imshow(image)
for polygon in polygons:
    vertices = [(polygon[0][i], polygon[0][i+1])
                for i in range(0, len(polygon[0]), 2)]
    text = polygon[1]
    patch = Polygon(vertices, closed=True, fill=False, linewidth=2, color='y')
    ax.axes.add_patch(patch)
    plt.text(vertices[0][0], vertices[0][1], text, fontsize=20, va="top")
plt.show()
