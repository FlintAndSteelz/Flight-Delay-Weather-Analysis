from pathlib import Path
import yaml 
import re # re =  regular expression 
import zipfile 
import pandas as pd 
# ============================================================
# PART 1 - PROJECT CONFIGURATION
# ============================================================

#1.1. Locate project root
PROJECT_ROOT = Path(__file__).resolve().parents[1]
#xác định project root (tức là địa chỉ chứa của repo)
# __file__ là một special variable trong  python, nó chứa đường dẫn đến file Python đang thực thi
# resolve() là method của đối tượng Path => nó chuyển dường dâ nx thành absoluate path đã được giải quyết

#1.2/ Locate configuration file 
CONFIG_PATH = PROJECT_ROOT / "cau_hinh.yaml"
# vd: PROJECT_ROOT / "data" / "raw" => return  "Flight-Delay-Weather-Analysis/data/raw"

#1.3. Check whether configuration file exits
#nếu mà teammate chưa tải cấu hình lamine yamal về thì tự động sẽ báo lỗi này 
if not CONFIG_PATH.is_file():
    raise FileNotFoundError(
        f"Configuration file not found: {CONFIG_PATH}"
    )

#1.4 Load project configuration
with open(CONFIG_PATH, "r", encoding = "utf-8") as file:
    config = yaml.safe_load(file)
    #yaml.safe_load() đọc nội dung Yaml và chuyển thành python objects 
    #sau khi đọc thì sẽ có dạng như: 
    """
    config = {
    "project": {
        "name": "Flight Delay and Weather Analysis",
        "airport": "JFK",
        "start_year": 2023,
        "end_year": 2025
    }
}
    """

#1.5 Validate configuration structure
if not isinstance(config, dict):
    raise ValueError(
        "Configuration must contain a YAML dictionary"
    )
# 1.6 Display basic information
print("\n" + "=" * 60)
print("PART 1 - PROJECT CONFIGURATION")
print("=" * 60)
print(f"Project root: {PROJECT_ROOT}")
print(f"Configuration file: {CONFIG_PATH}")
print(f"Configuration sections: {list(config.keys())}")
""" 
On_Time_Reporting_Carrier_On_Time_Performance_1987_present_2024_7.zip
Ta muốn python lấy ra 
year = 2024
month = 7
thì import re sẽ giúp ta nhận diện được 2024_7.zip 
Sau khi đọc cau_hinh.yaml ta sẽ lấy đường dẫn BTS 
data:
    bts:
        raw_dir: data/raw/bts 
BTS_DIR = PROJECT_ROOT / config["data"]["bts"]["raw_dir"] => trả về đường dẫn của folder chứa 48 file zip
tiếp theo là kiểm t ra xem folder BTS có thực sự tồn tại hay khôn
Tiếp theo là bước tìm tất cả các file zip
zip_files = sorted(BTS_DIR.glob("*.zip"))
glob() tìm những file khớp một pattern là zip: *  = bất kì chuỗi kí tự nào   |||  .zip  = phải kết thúc bằng với .zip
tức là sẽ chỉ lấy file .zip thoi  còn các file như .csv   .md thì khong lấy
và chúng ta cũng sẽ cần sort các đường dẫn lại theo từ nhỏ đến lớn 
Sau đó chúng ta in ra BTS directory và zip files found  
"""

# ============================================================
# PART 2 - BTS FILE DISCOVERY
# ============================================================
print("\n" + "=" * 60)
print("PART 2 - BTS FILE DISCOVERY")
print("=" * 60)

#2.1 Locate BTS Raw data directory 
BTS_DIR = PROJECT_ROOT / config['data']['bts']['raw_dir']

#2.2check whether bts directory exists
if not BTS_DIR.is_dir():
    raise FileNotFoundError(
        f"BTS directory not found: {BTS_DIR}"
    )

#2.3 Find all Zip files inside the BTS directory 
zip_files = sorted(BTS_DIR.glob("*.zip"))
print(f"BTS directory: {BTS_DIR}")
print(f"ZIP files found: {len(zip_files)}")
"""  
sau phần đầu thì ta có là: zip_files: list các path 
zip_files[0]: phần tử đầu tiên ở trong list 
zip_files[0].name: On_Time_Reporting_Carrier_On_Time_Performance_1987_present_2022_1.zip
pattern: r"(*\d*{4})_(*\d*{1,2})*\\.*zip$"
r -> raw_string:  
Sau khi tìm thấy pattern thì ta có thể lấy phần đã match
"""

#2.4 extract, add, and sort all 48 files zip into a parsed_files list 
parsed_files = []
unmatched_files = []
for zip_file in zip_files:
    match = re.search(
        r"(\d{4})_(\d{1,2})\.zip$",
        zip_file.name
    )
    if match:
        year = int(match.group(1))
        month = int(match.group(2))
        parsed_files.append(
            (year, month, zip_file)
        )
    else:
        unmatched_files.append(zip_file.name)

#2.5 thêm lệnh sort lại các tuple:
parsed_files.sort(key = lambda item: (item[0], item[1]))
#lambda item: (item[0], item[1]) -> với mỗi zip_file trong parsed_files ta thấy (year, month) làm key để xếp 

#2.6 display filename parsing results 
print("\n--- 2.6 Filename Parsing Results ---")
print(f"Successfully parsed files: {len(parsed_files)}")
print(f"unmatched files: {len(unmatched_files)}")

for year, month, zip_file in parsed_files:
    print(year, month, zip_file.name)

#2.7 filter 2023-2025 files 
#get analysis period from configuration
START_YEAR= config["project"]["start_year"]
END_YEAR = config["project"]['end_year']

#keep only files inside the main analysis period
analysis_files = []

for year, month, zip_file in parsed_files:
    if START_YEAR <= year <= END_YEAR:
        analysis_files.append(
            (year, month, zip_file)
        )

print("\n--- 2.7 Analysis Period ---")
print(f"Analysis period: {START_YEAR}-{END_YEAR}")
print(f"Analysis ZIP files: {len(analysis_files)}")

#2.8 check whether all expected months are present:

actual_months= {
    (year,month)
    for year, month, zip_file in analysis_files
}

expected_months = {
    (year,month)
    for year in range(START_YEAR, END_YEAR+1)
    for month in range(1,13)
}

missing_months = expected_months - actual_months 

print("\n--- 2.8 Monthly Coverage ---")
print(f"Expected months: {len(expected_months)}")
print(f"Actual unique months: {len(actual_months)}")
print(f"Missing months: {sorted(missing_months)}")

#2.9 check duplicate months

month_counts = {}

for year, month, zip_file in analysis_files:
    key = (year, month)
    if key not in month_counts:
        month_counts[key] = 1
    else:
        month_counts[key] +=1 

duplicate_months ={
    key: count 
    for key, count in month_counts.items()
    if count > 1

}

unexpected_months = actual_months - expected_months

print("\n--- 2.9 Duplicate and Unexpected Months ---")
print(f"Duplicate months: {duplicate_months}")
print(f"Unexpected months: {sorted(unexpected_months)}")


# ============================================================
# PART 3 - BTS ZIP VALIDATION
# ============================================================
print("\n" + "=" * 60)
print("PART 3 - BTS ZIP VALIDATION")
print("=" * 60)

#3.1 Select one zip file (to test)
print("\n--- 3.1-3.4 Single ZIP Validation ---")

if not analysis_files:
    raise ValueError("No analysis zip files found")

test_zip = analysis_files[0][2]
# analysis_files nó có nhiều cái tuple(year, month, zip_file) -> 0 -> 2 name 
print(f"\ntesting zip: {test_zip.name}")

#3.2 Open and inspect zip contents

""" 
zipfile.ZipFile() là một class trong module zipfile. 
khi mà gọi zipfile.ZipFile(test_zip, "r")
thì python tạo một object để đọc nội dung của zip
_ test_zip: đường dẫn zip cần mở
_ "r": read mode, chỉ đọc thôi, không thay đổi zip
_ .namelist() là method trả về một list các tên file và thư mục nằm bên trong ZIP 

"""

with zipfile.ZipFile(test_zip, "r") as zf: # -> mở zip file để đọc
    members = zf.namelist() # -> xem bên trong zip có những file nào
    print(f"Files inside Zip: {members}") # -> memebrs: list dùng để chứa tên các file bên trong zip 
    #3.3 Check zip integrity
    #method testzip() dùng để đọc dữ liệu của từng thành phần trong zip để kiểm tra crc và tính hợp lệ khi giải nén 
    #crc: cyclic redundancy check: là một giá trị dùng để kiểm tra dữ liệu có bị thay đổi hoặc hỏng hay không 
    # kq trả về là None: không phát hiện thành phần hỏng qua bài kiểm tra
    # kq trả về tên file: phát hiện thành phần hỏng qua bài kiểm tra
    # exception: zip này có thể không được hoặc không giải nén được 

    bad_file = zf.testzip()

    print(f"Corrupted member: {bad_file}")


    #3.4 check whether csv files are present 
    csv_files = []
    for name in members:
        if name.lower().endswith(".csv"):
            csv_files.append(name)
    print(f"CSV files found: {csv_files}")
    print(f"Number of csv files: {len(csv_files)}")


#3.5: validate all analysis ZIP files: phân loại các zip thành 2 nhóm: mở zip -> check integrity -> check csv files
#giả sử check 36 files zip mà file thứ n bị hỏng thì chương trình maybe dừng lại nên ta dùng try và except
valid_zip_files = [] #qualifed zip files
zip_issues = [] #bad zipfiels 
for year, month, zip_path in analysis_files:
    try:
        #open the current zip file
        with zipfile.ZipFile(zip_path, 'r') as zf:
            #check zip integrity 
            bad_file = zf.testzip()
            #get all members inside the ziop
            members = zf.namelist()
            #find csv files 
            csv_files = []
            for name in members:
                if name.lower().endswith(".csv"):
                    csv_files.append(name)

        #check validation results:
        if bad_file is not None:
            zip_issues.append(
                (year, month, zip_path.name, f"Corrupted: {bad_file}")
            )

        elif len(csv_files) != 1:
            zip_issues.append(
                (year, month, zip_path.name, f"CSV count: {len(csv_files)}")
            )
        else:
            valid_zip_files.append(
                (year, month, zip_path, csv_files[0])
            )

    except (zipfile.BadZipFile, OSError, RuntimeError, EOFError) as error:
        zip_issues.append(
            (year, month, zip_path.name, str(error))
        )


print("\n--- 3.5 All ZIP Validation Summary ---")

print(f"Valid ZIP files: {len(valid_zip_files)}")
print(f"ZIP files with issues: {len(zip_issues)}")
for issue in zip_issues:
    print(issue)

# ============================================================
# PART 4 - BTS CSV INSPECTION
# ============================================================
""" 
ở part trước chúng ta đã tạo ra valid_zip_files với mỗi phần tử có cấu trúc:
(year, month, zip_path, csv_name)
(
    2023,
    1,
    Path(".../2023_1.zip")
    "On_Time_Reporting_Carrier_..._2023_1.csv"
)

Mục tiêu ở part 4 này là tìm hiểu cấu trúc dữ liệu BTS trước khi tiến hành data cleaning 

1. 4.1 Read one BTS csv -> đọc dữ liệu csv từ file zip 
"""


#4.1 read one bts csv directly from zip
print("\n--- 4.1 Read One BTS CSV ---")

if not valid_zip_files:
    raise ValueError("No valid ZIP files available for inspection.")

year, month, zip_path, csv_name = valid_zip_files[0]
print(f"\n Inspecting BTS CSV: {year}-{month:02d}")
print(f"zip file: {zip_path.name}")
print(f"csv file: {csv_name}")


#Open the zip and read the csv inside
with zipfile.ZipFile(zip_path, 'r') as zf:
    with zf.open(csv_name) as csv_file:
        df_sample = pd.read_csv(
            csv_file,
            nrows = 1000,
            low_memory= False
        )
print("\n First 5 rows(first 10 columns): ")
print("-" * 60)
print(df_sample.iloc[:5, :10].to_string(index = False))

""" 
ở part 3, chúng ta dùng: zipfile.ZipFile(zip_path, "r") để mở zipfile
còn ở part 4: zf.open(csv_name) -> đây là lệnh dùng để mở file csv trong file zip 
"""

#4.2 Inspect Data frame shape, columns and data types
"""Khi đã có df_sample, ta cần biết df có bao nhiêu dòng, bao nhiêu cột và các cột có dữ liệu kiểu gì"""
print("\n --- 4.2 Dataframe structure")

#check the number of rows and columns
print(f"samples shape: {df_sample.shape}")  # df_sample trả về một cấu trúc tuple: (number of rows, number of columns)
print(f"Number of rows: {df_sample.shape[0]}")
print(f"Number of columns: {df_sample.shape[1]}")

#display all column names:
print("\n Column names: ")
for index, column in enumerate(df_sample.columns, start= 1):
    print(f"{index}. {column}")

#display data types:
print('\n column data types: ')
print(df_sample.dtypes.to_string())


# ============================================================
# 4.3 Identify Required BTS Columns
# ============================================================

print("\n -- 4.3 Rquired BTS columns: ")

required_columns = [
    "FlightDate", 
    "Reporting_Airline"
    "Flight_Number_Reporting_Airline",
    "Origin",
    "Dest",
    "CRSDepTime",
    "DepDelay",
    "DepDel15",
    "Cancelled",
    "Diverted",
    "Distance"
]
print(f"Number of required columns: {len(required_columns)}")

#4.3.2 check column availability 

available_columns =[]
missing_columns = []

for column in required_columns:
    if column in df_sample.columns:
        available_columns.append(column)
    else:
        missing_columns.append(column)

print(f"Available columns: {len(available_columns)}")
print(f"Missing columns: {len(missing_columns)}")

print('\n Available required columns: ')
for column in available_columns:
    print(f"    [OK] {column}")

print("\nMissing required columns:")
if not missing_columns:
    print("  None")
else:
    for column in missing_columns:
        print(f"  [MISSING] {column}")

