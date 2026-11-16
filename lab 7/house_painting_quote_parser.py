def clean_colour_name(name):
    """
    Converts a colour name into a lowercase code.
    Returns an empty string for invalid input.
    """
    if not isinstance(name, str):
        return ""

    return name.strip().lower().replace(" ", "_")


def room_area(text):
    """
    Converts LENGTHxWIDTH into square feet.
    Returns 0 for invalid input.
    """
    if not isinstance(text, str):
        return 0

    parts = text.lower().split("x")

    if len(parts) != 2:
        return 0

    length, width = parts

    if not length.strip().isdigit() or not width.strip().isdigit():
        return 0

    return int(length) * int(width)


def total_wall_area(text):
    """
    Adds valid wall areas separated by semicolons.
    Invalid entries are ignored.
    """
    if not isinstance(text, str):
        return 0

    total = 0

    for area in text.split(";"):
        area = area.strip()

        if area.isdigit():
            total += int(area)

    return total


def main():
    print("==== Running clean_colour_name ====")
    value = input("Enter a paint colour name (e.g. Ocean Blue): ")
    print("Colour code:", clean_colour_name(value))

    print("\n==== Running room_area ====")
    value = input("Enter room size as LENGTHxWIDTH in feet (e.g. 12x10): ")
    print("Room area (sq ft):", room_area(value))

    print("\n==== Running total_wall_area ====")
    value = input("Enter wall areas separated by ; (e.g. 120;95;110): ")
    print("Total wall area (sq ft):", total_wall_area(value))


if __name__ == "__main__":
    main()
