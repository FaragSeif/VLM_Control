import cv2

from serial_pipline import ExoConnection
from capture_stream import Capture
from vision_handler import VisionServer

exp_num = 100 # experiment number for Logging and video 

def get_weight_from_response(response):
    """
        A function to parse the VLM response and return the weight and object name
        Input:
            response(string): the string response return from the VLM
        Return:
            Tuple(int, string): a tuple of object weight in grams and the name of the object

    """
    response_content = response.choices[0].message.content
    response_content = response_content.split(", ")
    holding = response_content[0].split(": ")[1]

    if holding == "TRUE":
        weight = response_content[2].split(": ")[1]
        weight = int(weight.strip(" grams"))
        object_name = response_content[1].split(": ")[1]
        return weight, object_name
    else:
        return 0, "No Object"


def get_turns_from_weight(weight):
    """
        A function to do a linear mapping between the estimated weight and number of truns for the wearable device
        Input:
            weight(int): estimated weight in grams
        Returns:
            int: the number of truns to be sent to the wearable device
    """
    return int(weight * 30 / 3000)


Exo = ExoConnection(port="COM1", baudrate=115200) # Connection to the wearable device, comment it for testing the VLM only
cap = Capture("http://192.168.140.132:4747/video") # capture stream from an IP-camera, for testing a laptop or USB camera leave it empty
gpt_handler = VisionServer() # intitialize the OpenAI conneciton
frames = [] # Store frames for video logging


def main():
    try:
        object_name = "No Object"
        weight = 0
        while True:
            # Read the image
            status, image = cap.read()
            if not status:
                continue

            image = cv2.rotate(image, cv2.ROTATE_90_CLOCKWISE)
            # Send the image to the vision server to encode and send to GPT4v
            gpt_handler.update(image, "What is the weight of the object in the image?")
            if gpt_handler.response_flag:
                response = gpt_handler.value
                gpt_handler.response_flag = False
                weight, object_name = get_weight_from_response(response)
                # Send compensation value to the wearable device
                Exo.send_compensation("*-1,{}\n".format(repr(weight)).encode("Ascii")) # Comment for checking the VLM only
                print("weight compensation = ", weight, " kg", "Object: ", object_name)

            # Print the weight and name on the video stream
            cv2.putText(
                image,
                "Weight Estimated: " + str(weight) + "g",
                (0, 50),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0, 255, 0),
                4,
                cv2.LINE_AA,
            )
            cv2.putText(
                image,
                "Object: " + object_name,
                (0, 100),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (255, 255, 0),
                4,
                cv2.LINE_AA,
            )
            frames.append(image)
            cv2.imshow("OpenCV Feed", image)

            # break the loop if 'q' is pressed
            if cv2.waitKey(10) & 0xFF == ord("q"):
                break

    finally:
        # close all connections and resources, and save logging data
        Exo.send_compensation("*1,{}\n".format(repr(0)).encode("Ascii"))
        cv2.destroyAllWindows()
        print("Saving video...")
        frame_height, frame_width = frames[0].shape[:2]
        fourcc = cv2.VideoWriter_fourcc(*"XVID")
        out = cv2.VideoWriter(
            f"videos/experiment_{exp_num}.avi",
            fourcc,
            30.0,
            (frame_width, frame_height),
        )

        for frame in frames:
            out.write(frame)  # Write each frame to the output video

        out.release()
        print(f"Video saved successfully with {len(frames)} frames.")


if __name__ == "__main__":
    main()
