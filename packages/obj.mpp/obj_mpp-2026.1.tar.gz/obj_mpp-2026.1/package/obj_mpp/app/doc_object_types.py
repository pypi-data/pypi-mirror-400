"""
SEE COPYRIGHT, LICENCE, and DOCUMENTATION NOTICES: files
README-COPYRIGHT-utf8.txt, README-LICENCE-utf8.txt, and README-DOCUMENTATION-utf8.txt
at project source root.
"""

from obj_mpp.constant.catalog import MPM_CATALOG_SECTION
from obj_mpp.task.catalog.importer import ImportedElement

ROW_WIDTH = 35
TYPE_ROW_WIDTH = 14
FLOAT_PRECISION = 3


def Main() -> None:
    """"""
    model_t = ImportedElement(None, MPM_CATALOG_SECTION)

    mkpt_row_width = (
        max(class_type.__name__.__len__() for class_type in model_t.values()) - 2 + 4
    )
    empty_mkpt_class = mkpt_row_width * " "
    row_widths = (mkpt_row_width, ROW_WIDTH, TYPE_ROW_WIDTH) + 3 * (ROW_WIDTH,)
    hline = "+" + "+".join((row_width + 2) * "-" for row_width in row_widths) + "+"

    print(
        f"{hline}\n"
        f"| {'**Object**':{mkpt_row_width}} "
        f"| {'**Mark**':{ROW_WIDTH}} "
        f"| {'**Type**':{TYPE_ROW_WIDTH}} "
        f"| {'**Valid Range**':{ROW_WIDTH}} "
        f"| {'**Default Range**':{ROW_WIDTH}} "
        f"| {'**Default Precision**':{ROW_WIDTH}} |\n"
        f"{hline}\n"
        f"{hline}"
    )

    for element_name, element_t in model_t.items():
        print(f"| {element_name:{mkpt_row_width}} ", end="")

        model = element_t()
        for detail_idx, (name, value) in enumerate(model.items()):
            ini_name = f"``{name}``"
            mark_type = f"*{value.type.__name__}*"

            extreme_values = []
            if value.min_inclusive:
                extreme_values.append("[")
            else:
                extreme_values.append("]")
            if issubclass(value.type, float):
                extreme_values.append(
                    f"{value.min:.{FLOAT_PRECISION}}, {value.max:.{FLOAT_PRECISION}}"
                )
            else:
                extreme_values.append(f"{value.min}, {value.max}")
            if value.max_inclusive:
                extreme_values.append("]")
            else:
                extreme_values.append("[")

            if value.default_interval is None:
                default_interval = "None"
            else:
                if issubclass(value.type, float):
                    low_bound = f"{value.default_interval[0]:.{FLOAT_PRECISION}}"
                    high_bound = f"{value.default_interval[1]:.{FLOAT_PRECISION}}"
                else:
                    low_bound = value.default_interval[0]
                    high_bound = value.default_interval[1]
                default_interval = f"({low_bound}, {high_bound})"

            if value.default_precision is None:
                default_precision = "None"
            else:
                if issubclass(value.type, float):
                    default_precision = f"{value.default_precision:.{FLOAT_PRECISION}}"
                else:
                    default_precision = value.default_precision

            if detail_idx > 0:
                print(f"| {empty_mkpt_class} ", end="")
            print(
                f"| {ini_name:{ROW_WIDTH}} "
                f"| {mark_type:{TYPE_ROW_WIDTH}} "
                f"| {''.join(extreme_values):{ROW_WIDTH}} "
                f"| {default_interval:{ROW_WIDTH}} "
                f"| {default_precision:{ROW_WIDTH}} |\n"
                f"{hline}"
            )

        print(hline)


if __name__ == "__main__":
    #
    Main()
