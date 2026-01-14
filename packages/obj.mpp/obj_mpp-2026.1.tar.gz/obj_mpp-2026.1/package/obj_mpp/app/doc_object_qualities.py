"""
SEE COPYRIGHT, LICENCE, and DOCUMENTATION NOTICES: files
README-COPYRIGHT-utf8.txt, README-LICENCE-utf8.txt, and README-DOCUMENTATION-utf8.txt
at project source root.
"""

from obj_mpp.constant.catalog import Q_CATALOG_SECTION
from obj_mpp.task.catalog.importer import ImportedElement
from p_pattern.type.sampler.domain import educated_domain_t as domain_t

ROW_WIDTH = 35
TYPE_ROW_WIDTH = 14


def Main() -> None:
    """"""
    quality_context_t = ImportedElement(None, Q_CATALOG_SECTION)

    quality_row_width = (
        max(
            quality_class[0].__name__.__len__()
            for quality_class in quality_context_t.values()
        )
        - 2
        + 4
    )
    empty_quality_class = quality_row_width * " "
    row_widths = (quality_row_width, ROW_WIDTH, TYPE_ROW_WIDTH, ROW_WIDTH)
    hline = "+" + "+".join((row_width + 2) * "-" for row_width in row_widths) + "+"

    print(
        f"{hline}\n"
        f"| {'**Quality**':{quality_row_width}} "
        f"| {'**Parameter**':{ROW_WIDTH}} "
        f"| {'**Type**':{TYPE_ROW_WIDTH}} "
        f"| {'**Default Value**':{ROW_WIDTH}} |\n"
        f"{hline}\n"
        f"{hline}"
    )

    for quality_name, quality_class in quality_context_t.items():
        print(f"| {quality_name:{quality_row_width}} ", end="")

        value = quality_class[0](domain_t.New(((0, 1),)))
        value.SetKwargs({}, {})
        for kwargs in (value.s_kwargs, value.q_kwargs):
            if kwargs is None:
                continue

            subsequent = False
            for name, value in kwargs.items():
                if name.startswith("_"):
                    continue

                if subsequent:
                    print(f"| {empty_quality_class} ", end="")
                else:
                    subsequent = True
                print(
                    f"| {name:{ROW_WIDTH}} "
                    f"| {TYPE_ROW_WIDTH * ' '} "
                    f"| {value:{ROW_WIDTH}} |\n"
                    f"{hline}"
                )

        print(hline)


if __name__ == "__main__":
    #
    Main()
