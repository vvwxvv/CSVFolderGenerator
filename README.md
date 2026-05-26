# CSV Folder Generator

```
  ____  ______     __  _____     _     _           
 / ___||  _ \ \   / / |  ___|__ | | __| | ___ _ __ 
| |    | |_) \ \ / /  | |_ / _ \| |/ _` |/ _ \ '__|
| |___ |  __/ \ V /   |  _| (_) | | (_| |  __/ |   
 \____||_|     \_/    |_|  \___/|_|\__,_|\___|_|   
  ____                           _                  
 / ___| ___ _ __   ___ _ __ __ _| |_ ___  _ __      
| |  _ / _ \ '_ \ / _ \ '__/ _` | __/ _ \| '__|     
| |_| |  __/ | | |  __/ | | (_| | || (_) | |        
 \____|\___|_| |_|\___|_|  \__,_|\__\___/|_|        
```

Generate folders automatically from your CSV data.
Pick one or two column headers, choose a separator, and the tool
creates lowercase folders named after the values in those columns.

---

## Requirements

- Python 3.8+
- PyQt5

```
pip install PyQt5
```

---

## File Structure

```
project/
|-- src/
|   |-- assets/
|   |   +-- create_folders.py          <- core logic
|   +-- uiitems/
|       +-- close_button.py
|-- static/
|   +-- logo_imgs/
|       +-- cover.png
+-- csv_folder_generator_app.py        <- UI entry point
```

---

## How to Run

```
python csv_folder_generator_app.py
```

---

## UI Walkthrough

```
+--------------------------------------------------+
|                                            [ X ] |
|                  [ LOGO ]                        |
|                                                  |
|  Header 1  [______________________________]      |
|  Header 2  [______________________________]      |
|                                                  |
|  Separator  [ _ (underscore)          [v] ]      |
|                                                  |
|  [ Select CSV File         ]                     |
|    No CSV file selected                          |
|                                                  |
|  [ Select Output Folder    ]                     |
|    No output folder selected                     |
|                                                  |
|  [ Start Creating Folders  ]                     |
+--------------------------------------------------+
```

### Step-by-step

```
  STEP 1  ->  Type the column name from your CSV into "Header 1"
              This field is required.

  STEP 2  ->  (Optional) Type a second column name into "Header 2"
              Leave blank to use only one column.

  STEP 3  ->  Choose a separator from the dropdown:
                _   underscore   (default)
                -   dash
                .   dot
                    space

  STEP 4  ->  Click "Select CSV File" and pick your .csv file.

  STEP 5  ->  (Optional) Click "Select Output Folder".
              If skipped, folders are created in:
              <csv_directory>/generated_folders/

  STEP 6  ->  Click "Start Creating Folders".
              A success message will show how many folders were made.
```

---

## Folder Naming Rules

```
  Rule 1  ->  All text is converted to lowercase
  Rule 2  ->  The two column values are joined by your chosen separator
  Rule 3  ->  Invalid characters ( < > : " / \ | ? * ) are replaced with _
  Rule 4  ->  Leading and trailing spaces or dots are trimmed
  Rule 5  ->  Rows where both selected columns are empty are skipped
```

---

## CSV Format

Your CSV must have a header row. Column names are case-sensitive.

```
Example CSV (artworks.csv):

  artist          | title                        | year
  ----------------+------------------------------+------
  Wang Wei        | Cloud Rest                   | 2021
  Li Hua          | Morning in the Western Garden| 2020
  Zhang Ming      | Floating Clouds              | 2022
  Chen Bo         |                              | 2019   <- skipped (empty title)
```

---

## Examples

### Example A -- One header, underscore (default)

```
  Header 1   :  title
  Header 2   :  (empty)
  Separator  :  _
  CSV        :  artworks.csv
  Output     :  ./output/

  Result folders:
    output/
    |-- cloud_rest/
    |-- morning_in_the_western_garden/
    +-- floating_clouds/
```

---

### Example B -- Two headers, underscore

```
  Header 1   :  artist
  Header 2   :  title
  Separator  :  _
  CSV        :  artworks.csv
  Output     :  ./output/

  Result folders:
    output/
    |-- wang_wei_cloud_rest/
    |-- li_hua_morning_in_the_western_garden/
    +-- zhang_ming_floating_clouds/
```

---

### Example C -- Two headers, dash separator

```
  Header 1   :  year
  Header 2   :  title
  Separator  :  -
  CSV        :  artworks.csv
  Output     :  ./output/

  Result folders:
    output/
    |-- 2021-cloud_rest/
    |-- 2020-morning_in_the_western_garden/
    +-- 2022-floating_clouds/
```

---

### Example D -- Two headers, dot separator

```
  Header 1   :  artist
  Header 2   :  year
  Separator  :  .
  CSV        :  artworks.csv
  Output     :  ./output/

  Result folders:
    output/
    |-- wang_wei.2021/
    |-- li_hua.2020/
    +-- zhang_ming.2022/
```

---

## Error Messages

```
  "Please enter at least Header 1."
  -> Header 1 input is empty. Fill it in before starting.

  "Please select a CSV file."
  -> No CSV has been chosen. Use "Select CSV File".

  "Column(s) not found in CSV: ['xyz']"
  -> The header name you typed does not match any column in your CSV.
     Check spelling and letter case (case-sensitive).

  "An error occurred: ..."
  -> Unexpected error. The full message is shown for diagnosis.
```

---

## Core Logic Reference  (create_folders.py)

```python
create_folders_from_csv(
    csv_file  = "artworks.csv",   # path to CSV
    headers   = ["artist","title"],# 1 or 2 column names
    base_path = "./output",        # root folder for output
    separator = "_",               # join character
)
```

Can also be used directly from Python without the UI.

---

## Notes

```
  (*)  Column names are case-sensitive.
       "Title" and "title" are treated as different columns.

  (*)  The output folder is created automatically if it does not exist.

  (*)  Existing folders with the same name are kept (not overwritten).

  (*)  Rows with empty values in both selected columns are skipped
       and reported in the console with their row numbers.
```

---