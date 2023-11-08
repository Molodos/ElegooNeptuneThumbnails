class ColorList:

    def __init__(self):
        self._color_list: dict[int, int] = dict()

    def get_length(self) -> int:
        return len(self._color_list)

    def add_color(self, color: int) -> bool:
        if self.get_length() < 1024:
            self._color_list[color] = self._color_list.get(color, 0) + 1
            return True
        return False

    def get_sorted_entries(self) -> list[tuple[int, int, int, int, int]]:
        # Color, r, g, b, count
        sorted_entries: list[tuple[int, int, int, int, int]] = list()
        for color, count in sorted(self._color_list.items(), key=lambda x: x[1], reverse=True):
            b: int = color & 255
            g: int = (color >> 8) & 255
            r: int = (color >> 16) & 255
            sorted_entries.append((color, r, g, b, count))
        return sorted_entries


def col_pic_encode(input_color_16: list[int], color_list: ColorList, output_max_size: int, colors_max: int) -> int:
    colors_max = max(1024, colors_max)
    for color in input_color_16:
        color_list.add_color(color=color)
    for color, r, g ,b, count in color_list.get_sorted_entries()[::-1]:
        pass
    return 0


def col_pic_encode_str(input_color_16: list[int], output_data: str, output_max_size: int, colors_max: int) -> int:
    color_list: ColorList = ColorList()
    encoded_len: int = col_pic_encode(input_color_16, color_list, output_max_size, colors_max)
    # TODO
    return encoded_len
