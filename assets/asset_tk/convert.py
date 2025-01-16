import os
import subprocess

cells = ["0.svg", "1.svg", "2.svg", "3.svg", "4.svg", "5.svg", "6.svg", "7.svg", "8.svg",
         "bomb.svg", "bomb_red.svg", "bomb_wrong.svg", "flag.svg", "closed.svg", "no_guess.svg", "there_is_bomb.svg"]
cells_size = "24x24"

segment_led = ["LED_0.svg", "LED_1.svg", "LED_2.svg", "LED_3.svg", "LED_4.svg", "LED_5.svg", "LED_6.svg", "LED_7.svg", "LED_8.svg", "LED_9.svg"]
segment_size = "18x34"

face_svg = ["face_unpressed.svg", "face_lose.svg", "face_win.svg"]
face_size = "38x38"


def resize_svg(list_svg: list[str], size: str):
    for svg_file in list_svg:
        if os.path.exists(svg_file):
            png_file = svg_file.replace('.svg', '.png')
            command = f'magick +antialias {svg_file} -resize {size} -quality 100 -channel RGB {png_file}'
            subprocess.run(command, shell=True)
        else:
            print(f"File {svg_file} does not exist.")


if __name__ == '__main__':
    resize_svg(cells, cells_size)
    resize_svg(segment_led, segment_size)
    resize_svg(face_svg, face_size)
