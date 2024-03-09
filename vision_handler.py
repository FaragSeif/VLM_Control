# import openai.types.create_embedding_response
import cv2  # We're using OpenCV to read video, to install !pip install opencv-python
import threading
import base64
from openai import OpenAI


class VisionServer:
    def __init__(self, stream=False):
        self.client = OpenAI(api_key="OpenAI-Key")  # GPT API
        self.model = "gpt-4-vision-preview"
        self.state = True
        self.stream = stream
        self.response_flag = False
        self.value = None
        self.system_prompt = "Below is an image which includes a hand and an object, your task is to determine if the hand in the image is holding an object or not, and if so, estimate the mass of this object:\n \
                            1- First, you should determine if there is a hand in the image\n \
                            2- Second, you should determine if the hand is holding an object\n \
                            3- Third, if the hand is indeed holding an object, you should estimate the mass of that object\n \
                            4- Your answer should always include the TRUE if hand is holding an object, or FALSE if not holding an object\n \
                            5- Your answer should always include the mass in grams, or '0' if no object can be found\n \
                            6- Your answer should always include the name or category of the object being held.\n \
                            7- There are ONLY 5 types of answers, a Drill, a Hammer, a Staple gun, Pliers, and No object if you cannot find a hand\n \
                            YOU ARE ONLY ALLOWED TO RESPOND IN THE FOLLOWING FORMAT 'Holding: <TRUE or FALSE>, Object: <object_name>, Weight: <object_estimated_weight>', and the MAXIMUM object_estimated_weight is '3000 grams.'\n \
                            Here are multiple examples for different situations:\n \
                            example 1 (person holding a Hammer in his right hand):\n \
                            User: What is the weight of the object in the image?\n \
                            Assistant: Holding: TRUE, Object: Hammer, Weight: 400 grams\n \
                            example 2 (person in the image but his hands are not visible):\n \
                            User: What is the weight of the object in the image?\n \
                            Assistant: Holding: FALSE, Object: None, Weight: 0 grams\n \
                            example 3 (person holding a drill in his right hand):\n \
                            User: What is the weight of the object in the image?\n \
                            Assistant: Holding: TRUE, Object: Drill, Weight: 1870 grams\n \
                            example 4 (person holding a staple gun in his right hand):\n \
                            User: What is the weight of the object in the image?\n \
                            Assistant: Holding: TRUE, Object: Staple Gun, Weight: 650 grams\n \
                            example 1 (person holding Pliers in his right hand):\n \
                            User: What is the weight of the object in the image?\n \
                            Assistant: Holding: TRUE, Object: Pliers, Weight: 170 grams"

    def analyze(self, image, prompt):

        _, buffer = cv2.imencode(".jpeg", image)
        base64_image = base64.b64encode(buffer).decode("utf-8")

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": self.system_prompt,
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt,
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}",
                                "detail": "low",
                            },
                        },
                    ],
                },
            ],
            temperature=0.5,
            max_tokens=25,
        )

        self.response_flag = True
        self.value = response
        self.state = True

    def update(self, image, prompt):

        if self.state == True:
            t = threading.Thread(target=self.analyze, args=(image, prompt), daemon=True)
            t.start()
            self.state = False
