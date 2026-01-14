import os
import easyocr

# Initialize EasyOCR
reader = easyocr.Reader(['en'])

# Paths
folder_path = r"C:\Users\chuck\OneDrive\Desktop\COURT\KELSEY TEXTS"
output_file = r"C:\Users\chuck\OneDrive\Desktop\COURT\kelsey_texts_output.txt"

def extract_chat_text(folder, out_file):
    with open(out_file, "w", encoding="utf-8") as f_out:
        for filename in os.listdir(folder):
            if filename.lower().endswith((".png", ".jpg", ".jpeg")):
                img_path = os.path.join(folder, filename)
                try:
                    results = reader.readtext(img_path, detail=1)  # [bbox, text, conf]
                    f_out.write(f"\n--- Extracted from {filename} ---\n")
                    
                    current_name = None
                    for bbox, text, conf in results:
                        text = text.strip()
                        if not text:
                            continue
                        
                        # Heuristic: if text looks like a name (short, capitalized, few words)
                        if len(text.split()) <= 3 and text[0].isupper():
                            current_name = text
                            f_out.write(f"\n{text}:\n")
                        else:
                            if current_name:
                                f_out.write(f"{text}\n")
                            else:
                                f_out.write(f"(Unknown): {text}\n")
                    
                    print(f"Processed: {filename}")
                except Exception as e:
                    print(f"Error with {filename}: {e}")

extract_chat_text(folder_path, output_file)
print(f"\nAll text extracted and saved to: {output_file}")
