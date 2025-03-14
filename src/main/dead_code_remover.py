from pathlib import Path

# from collections import defaultdict
# import json

# with open("om.json", "r", encoding="utf-8") as f:
#     om = json.load(f)

# dir2func: dict[Path, list[dict]] = defaultdict(list)

# for func_metadata in om["func_metadata"]:
#     if ".rustup/toolchains" in func_metadata["define_path"]:
#         continue
#     dir2func[Path(func_metadata["define_path"])].append(func_metadata)

# for k in dir2func.keys():
#     dir2func[k] = sorted(dir2func[k], key=lambda x: int(x["line_num"]))

# for k, v in dir2func.items():
#     print(k)
#     with open(k, "r", encoding="utf-8") as f:
#         content = f.readlines()
#     for each in v:
#         print(f"\t{each['def_id']}, line_num = {each['line_num']}")
#         content[each["line_num"]] = content[each["line_num"]].strip() + f"/* used */\n"
#     with open(k, "w", encoding="utf-8") as f:
#         f.writelines(content)

from re import search
import json
from collections import defaultdict
from bisect import bisect_left


def find_rust_func_span(lines: list[str], lo: int) -> tuple[int, int]:
    hi: int = lo
    curly_brackets: int = 0
    while curly_brackets == 0:
        if lines[hi].lstrip() == "//":
            hi += 1
            continue
        curly_brackets += lines[hi].count("{")
        if curly_brackets > 0:
            curly_brackets -= lines[hi].count("}")
            hi += 1
            break  # 函数签名后的函数体开始了
        elif lines[hi].rstrip().endswith(";"):
            # trait方法
            return (lo, hi + 1)
        else:
            curly_brackets -= lines[hi].count("}")
            hi += 1
    while curly_brackets > 0:
        curly_brackets += lines[hi].count("{") - lines[hi].count("}")
        hi += 1
    return (lo, hi)


with open("om.json", "r", encoding="utf-8") as f:
    om = json.load(f)

dir_tree: defaultdict[Path, list[int]] = defaultdict(list)

for each in om["func_metadata"]:
    if ".rustup/toolchains" in each["define_path"]:
        continue
    dir_tree[Path(each["define_path"])].append(each["line_num"])

del om

for source_code_path, func_infos in dir_tree.items():
    func_infos.sort()
    with open(source_code_path, "r", encoding="utf-8") as f:
        content = f.readlines()
    for line_num, line in enumerate(content):
        if search(r"fn [a-zA-Z_][a-zA-Z_\d]+\(", line) is not None:
            # 是函数定义
            span = find_rust_func_span(content, line_num)
            if any([x for x in func_infos if x == span[0]]):
                # 是活跃代码
                continue
            else:
                print(f"Dead code found in {source_code_path}!")
                for i in range(span[0], span[1]):
                    content[i] = f"// {content[i]}"
                    # print(f"{i:04d}|{content[i].rstrip()}")
    with open(source_code_path, "w", encoding="utf-8") as f:
        f.writelines(content)
    del content
