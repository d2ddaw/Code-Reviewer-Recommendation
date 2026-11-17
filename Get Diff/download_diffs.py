import csv
import hashlib
import json
import time
from pathlib import Path
from urllib.parse import quote, unquote

import requests
from openpyxl import load_workbook
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


# 修改为你的 Excel 路径
EXCEL_PATH = Path(
    r"Code Reviewer Recommendation\DataSet\Data of Code Snippets in Code Review.xlsx"
)

# diff 和结果清单的保存位置
OUTPUT_DIR = Path(r"Code Reviewer Recommendation\diff_result")
DIFF_DIR = OUTPUT_DIR / "diffs"
MANIFEST_PATH = OUTPUT_DIR / "manifest.csv"

BASE_URL = "https://review.opendev.org"

# 控制请求速度，避免对服务器造成过大压力
REQUEST_INTERVAL_SECONDS = 0.3


def make_session():
    """创建支持自动重试的 HTTP 会话。"""
    retry = Retry(
        total=3,
        backoff_factor=2,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET"],
        respect_retry_after_header=True,
    )

    session = requests.Session()
    session.headers.update({
        "User-Agent": "OpenStack-Review-Research/1.0",
    })
    session.mount("https://", HTTPAdapter(max_retries=retry))
    return session


def read_unique_records(excel_path):
    """读取所有工作表，并按变更、版本和文件去重。"""
    workbook = load_workbook(excel_path, read_only=True, data_only=True)
    records = {}

    try:
        for sheet in workbook.worksheets:
            rows = sheet.iter_rows(values_only=True)
            headers = next(rows, None)

            if not headers:
                continue

            columns = {
                str(value).strip(): index
                for index, value in enumerate(headers)
                if value is not None
            }

            required = ["Change_id", "Patch_set", "File"]
            missing = [name for name in required if name not in columns]
            if missing:
                print(f"跳过工作表 {sheet.title}：缺少列 {missing}")
                continue

            for row_number, row in enumerate(rows, start=2):
                change_id = row[columns["Change_id"]]
                patch_set = row[columns["Patch_set"]]
                file_path = row[columns["File"]]

                if not all(value is not None and str(value).strip()
                           for value in (change_id, patch_set, file_path)):
                    continue

                # 避免 Excel 中的数字 2.0 被拼成无效的版本号
                if isinstance(patch_set, float) and patch_set.is_integer():
                    patch_set = int(patch_set)

                change_id = str(change_id).strip()
                patch_set = str(patch_set).strip()
                file_path = str(file_path).strip()

                # Change_id 可能已包含 %2F，先解码后再统一编码
                normalized_change = unquote(change_id)
                key = (normalized_change, patch_set, file_path)

                if key not in records:
                    records[key] = {
                        "sheet": sheet.title,
                        "first_excel_row": row_number,
                        "change_id": normalized_change,
                        "patch_set": patch_set,
                        "file_path": file_path,
                    }
    finally:
        workbook.close()

    return list(records.values())


def build_url(record):
    change_id = quote(record["change_id"], safe="~")
    patch_set = quote(record["patch_set"], safe="")
    file_path = quote(record["file_path"], safe="")

    return (
        f"{BASE_URL}/changes/{change_id}"
        f"/revisions/{patch_set}/files/{file_path}/diff"
    )


def output_filename(record):
    """根据组合生成稳定的文件名，便于重复运行时跳过已有文件。"""
    key = "\n".join([
        record["change_id"],
        record["patch_set"],
        record["file_path"],
    ])
    digest = hashlib.sha256(key.encode("utf-8")).hexdigest()
    return f"{digest}.json"


def parse_gerrit_json(text):
    # Gerrit 通常在 JSON 前添加一行安全前缀：)]}'
    if text.startswith(")]}'"):
        text = text.split("\n", 1)[1]
    return json.loads(text)


def main():
    if not EXCEL_PATH.exists():
        print(f"找不到 Excel 文件：{EXCEL_PATH}")
        return

    DIFF_DIR.mkdir(parents=True, exist_ok=True)
    records = read_unique_records(EXCEL_PATH)
    total = len(records)

    print(f"共有 {total} 个去重后的变更、版本和文件组合。")

    session = make_session()
    results = []
    success_count = 0
    failure_count = 0

    try:
        for index, record in enumerate(records, start=1):
            url = build_url(record)
            filename = output_filename(record)
            output_path = DIFF_DIR / filename

            result = {
                **record,
                "status": "",
                "diff_file": str(Path("diffs") / filename),
                "url": url,
                "error": "",
            }

            # 支持中断后重新运行；验证已有文件确实是 JSON
            if output_path.exists():
                try:
                    with output_path.open("r", encoding="utf-8") as f:
                        json.load(f)
                    result["status"] = "already_downloaded"
                    success_count += 1
                    results.append(result)
                    print(f"[{index}/{total}] 已存在：{record['file_path']}")
                    continue
                except (OSError, json.JSONDecodeError):
                    pass

            try:
                response = session.get(url, timeout=30)
                response.raise_for_status()
                diff_data = parse_gerrit_json(response.text)

                # 先写临时文件，写完再重命名，避免中断时留下不完整结果
                temp_path = output_path.with_suffix(".tmp")
                with temp_path.open("w", encoding="utf-8") as f:
                    json.dump(diff_data, f, ensure_ascii=False, indent=2)
                temp_path.replace(output_path)

                result["status"] = "downloaded"
                success_count += 1
                print(f"[{index}/{total}] 成功：{record['file_path']}")

            except (requests.RequestException, ValueError, OSError) as error:
                result["status"] = "failed"
                result["diff_file"] = ""
                result["error"] = str(error)
                failure_count += 1
                print(f"[{index}/{total}] 失败：{error}")

            results.append(result)
            time.sleep(REQUEST_INTERVAL_SECONDS)

    except KeyboardInterrupt:
        print("\n已中断，正在保存目前的结果清单。")

    finally:
        session.close()

        fieldnames = [
            "sheet",
            "first_excel_row",
            "change_id",
            "patch_set",
            "file_path",
            "status",
            "diff_file",
            "url",
            "error",
        ]

        with MANIFEST_PATH.open("w", encoding="utf-8-sig", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)

        print(f"\n已获取或已存在：{success_count}")
        print(f"失败：{failure_count}")
        print(f"结果清单：{MANIFEST_PATH}")
        print(f"diff 文件夹：{DIFF_DIR}")


if __name__ == "__main__":
    main()