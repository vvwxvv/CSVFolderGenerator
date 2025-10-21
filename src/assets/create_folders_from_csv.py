import sys
import os
import csv
from pathlib import Path
from src.uiitems.close_button import CloseButton


def create_folders_from_csv_language_en(csv_file, header_mapping, base_path='.', separator='_', filter_language='EN'):
    """
    Read CSV file and create folders based on custom header names.
    Only processes rows where language column is 'EN'.
    """
    created_folders = []
    skipped_rows = 0
    
    Path(base_path).mkdir(parents=True, exist_ok=True)
    
    try:
        with open(csv_file, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            
            csv_headers = reader.fieldnames
            missing_headers = [h for h in header_mapping if h not in csv_headers]
            
            if missing_headers:
                raise ValueError(f"Headers not found in CSV: {missing_headers}")
            
            if 'language' not in csv_headers:
                raise ValueError("CSV must have a 'language' column for filtering")
            
            for row_num, row in enumerate(reader, start=2):
                language = row.get('language', '').strip().upper()
                if language != filter_language.upper():
                    skipped_rows += 1
                    continue
                
                folder_parts = []
                for header in header_mapping:
                    value = row.get(header, '').strip()
                    if value:
                        folder_parts.append(value)
                
                if not folder_parts:
                    continue
                
                folder_name = separator.join(folder_parts)
                folder_name = sanitize_folder_name(folder_name)
                folder_path = os.path.join(base_path, folder_name)
                
                try:
                    Path(folder_path).mkdir(parents=True, exist_ok=True)
                    created_folders.append(folder_path)
                except Exception as e:
                    print(f"Error creating folder '{folder_path}': {e}")
            
        print(f"Skipped {skipped_rows} rows (non-EN language)")
        return created_folders
        
    except FileNotFoundError:
        raise FileNotFoundError(f"CSV file '{csv_file}' not found")
    except Exception as e:
        raise Exception(f"Error processing CSV: {e}")


def create_folders_from_csv_auto_en(csv_file, header_mapping, base_path='.', separator='_'):
    """
    Read CSV file and create folders based on custom header names.
    Automatically appends '_en' to headers except for 'year' and 'size'.
    """
    created_folders = []
    no_suffix_headers = ['year', 'size']
    
    Path(base_path).mkdir(parents=True, exist_ok=True)
    
    try:
        with open(csv_file, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            csv_headers = reader.fieldnames
            
            actual_headers = []
            for header in header_mapping:
                if header.lower() in no_suffix_headers:
                    actual_headers.append(header)
                else:
                    actual_headers.append(f"{header}_en")
            
            missing_headers = [h for h in actual_headers if h not in csv_headers]
            
            if missing_headers:
                raise ValueError(f"Headers not found in CSV: {missing_headers}")
            
            for row_num, row in enumerate(reader, start=2):
                folder_parts = []
                for header in actual_headers:
                    value = row.get(header, '').strip()
                    if value:
                        folder_parts.append(value)
                
                if not folder_parts:
                    continue
                
                folder_name = separator.join(folder_parts)
                folder_name = sanitize_folder_name(folder_name)
                folder_path = os.path.join(base_path, folder_name)
                
                try:
                    Path(folder_path).mkdir(parents=True, exist_ok=True)
                    created_folders.append(folder_path)
                except Exception as e:
                    print(f"Error creating folder '{folder_path}': {e}")
            
        return created_folders
        
    except FileNotFoundError:
        raise FileNotFoundError(f"CSV file '{csv_file}' not found")
    except Exception as e:
        raise Exception(f"Error processing CSV: {e}")


def sanitize_folder_name(name):
    """
    Remove or replace invalid characters for folder names.
    """
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        name = name.replace(char, '_')
    name = name.strip('. ')
    return name
