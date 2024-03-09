import cv2

from serial_pipline import ExoConnection
from capture_stream import Capture
from vision_handler import VisionServer

exp_num = 3


def get_weight_from_response(response):
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
    # if the map is linear, so the formula is turns = weight * 30 / 3000
    return int(weight * 30 / 3000)


Exo = ExoConnection(port="COM1", baudrate=115200)
cap = Capture("http://192.168.140.132:4747/video")
gpt_handler = VisionServer()
frames = []


def main():
    try:
        object_name = "No Object"
        weight = 0
        while True:
            status, image = cap.read()
            if not status:
                continue

            image = cv2.rotate(image, cv2.ROTATE_90_CLOCKWISE)
            gpt_handler.update(image, "What is the weight of the object in the image?")
            if gpt_handler.response_flag:
                response = gpt_handler.value
                gpt_handler.response_flag = False
                weight, object_name = get_weight_from_response(response)
                Exo.send_compensation("*-1,{}\n".format(repr(weight)).encode("Ascii"))
                print("weight compensation = ", weight, " kg", "Object: ", object_name)

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
