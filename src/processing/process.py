import os
import shutil
from PIL import Image
import numpy as np
from src.processing.process_fields import process_fields
from src.processing.filtre import capitalize_words

global eff_ocr
eff_ocr = False  # Setează True dacă EfficientOCR este disponibil, altfel False
ocr_type_announced = False  # Variabilă pentru a afișa tipul OCR doar o dată

if eff_ocr == True:
    try:
        from efficient_ocr import EffOCR
    except ImportError:
        print("EfficientOCR nu este disponibil în process.py")
        EffOCR = None
else:
    import easyocr
    
reader = None  # Inițializăm variabila reader

def set_reader(ocr_reader):
    global reader
    reader = ocr_reader


# Funcția pentru procesarea unei zone
def proceseaza_zona(coord, idx, image):
    zona_decupata = image.crop(coord)  # Decupează zona
    if idx==15:
        zona_decupata = zona_decupata.resize((zona_decupata.width * 2, zona_decupata.height * 2))  # Mărire imagine
    else:
        zona_decupata = zona_decupata.resize((zona_decupata.width * 3, zona_decupata.height * 3))
    #save cropped image for debug in debug_media 
    debug_on = False  # Setează True pentru a activa debug-ul
    if debug_on==True:
        debug_media_folder = "debug_media"
        os.makedirs(debug_media_folder, exist_ok=True)  # Creează folderul debug_media dacă nu există
        zona_decupata.save(os.path.join(debug_media_folder, f"debug_cropped_{idx}.jpg"))  # Salvează imaginea decupată pentru debug
        # Mărim imaginea decupată pentru a îmbunătăți OCR-ul
        zona_decupata = zona_decupata.resize((zona_decupata.width * 3, zona_decupata.height * 3))  # Mărire imagine
        #save resized image for debug in debug_media folder
        zona_decupata.save(os.path.join(debug_media_folder, f"debug_resized_{idx}.jpg"))  # Salvează imaginea mărită pentru debug
    
    zona_np = np.array(zona_decupata)  # convert in numpy array
    
    # Verificăm tipul de reader și folosim metoda corespunzătoare
    global ocr_type_announced
    
    try:
        # Verificăm dacă reader-ul are metoda 'infer' (specifică pentru EfficientOCR)
        if hasattr(reader, 'infer') and eff_ocr == True:
            # Folosim EfficientOCR
            if not ocr_type_announced:
                print("Se folosește EfficientOCR pentru toate zonele OCR")
                ocr_type_announced = True
            rezultate = reader.infer(zona_np)
            text = rezultate if isinstance(rezultate, str) else str(rezultate)
        else:
            # Folosim EasyOCR (fallback)
            if not ocr_type_announced:
                print("Se folosește EasyOCR pentru toate zonele OCR")
                ocr_type_announced = True
            rezultate = reader.readtext(zona_np)
            text = " ".join([rezultat[1] for rezultat in rezultate])  # extract text from results
    except Exception as e:
        if not ocr_type_announced:
            print(f"Eroare la inițializarea OCR: {e}")
            print("Se va folosi EasyOCR ca fallback pentru toate zonele")
            ocr_type_announced = True
        # Fallback la EasyOCR dacă EfficientOCR eșuează
        try:
            rezultate = reader.readtext(zona_np)
            text = " ".join([rezultat[1] for rezultat in rezultate])
        except Exception as e2:
            print(f"Eroare critică la OCR pentru zona {idx}: {e2}")
            text = ""  # Return empty string if both fail
    
    # print(f"OCR text pentru zona {idx}: {text}")  # Comentat pentru a reduce output-ul
    return text

# Funcția pentru procesarea fișierelor
def proceseaza_fisier(image_path, output_folder, coordonate):
    # Reset variabila pentru afișarea tipului OCR pentru fiecare fișier nou
    global ocr_type_announced
    ocr_type_announced = False
    
    image = Image.open(image_path)  # Încarcă imaginea
    print(f"Procesăm fișierul: {image_path}")  # Debug: Afișăm numele fișierului procesat

    # Inițializăm variabilele pentru fiecare câmp
    strada, numar, localitate, judet, bloc, scara, etaj, apartament, cp, prenume, nume, cnp_total, email, phone, doiani = [""] * 15
    initiala_tatalui = ""
    folder_localitate_sec = ""
    temp_folder_localitate_mare = ""
    temp_folder_localitate_med = ""
    temp_folder_localitate_mic = ""
    folder_localitate = ""
    folder_localitate_mare = ""
    folder_localitate_med = ""
    folder_localitate_mic = ""

    # Parcurgem coordonatele și procesăm fiecare zonă
    for idx, coord in enumerate(coordonate):
        text_initial = proceseaza_zona(coord, idx, image)
        temp_prenume, temp_nume, temp_initiala_tatalui, temp_strada, temp_numar, temp_cnp_total, temp_email, temp_judet, temp_localitate, temp_cp, temp_bloc, temp_scara, temp_etaj, temp_apartament, temp_phone, temp_doiani, temp_folder_localitate_mic, temp_folder_localitate_med, temp_folder_localitate_mare = process_fields(text_initial, idx, False)  # debug_switch este True pentru debug
        # Atribuire valorilor returnate la variabilele finale
        if temp_prenume:
            prenume = temp_prenume
        if temp_nume:
            nume = temp_nume
        if temp_initiala_tatalui:
            initiala_tatalui = temp_initiala_tatalui
        if temp_strada:
            strada = temp_strada
        if temp_numar:
            numar = temp_numar
        if temp_cnp_total:
            cnp_total = temp_cnp_total
        if temp_email:
            email = temp_email
        if temp_judet:
            judet = temp_judet
        if temp_localitate:
            localitate = temp_localitate
        if temp_cp:
            cp = temp_cp
        if temp_bloc:
            bloc = temp_bloc
        if temp_scara:
            scara = temp_scara
        if temp_etaj:
            etaj = temp_etaj
        if temp_apartament:
            apartament = temp_apartament
        if temp_phone:
            phone = temp_phone
        if temp_doiani:
            doiani = temp_doiani
        if temp_folder_localitate_mic:
            folder_localitate_mic = temp_folder_localitate_mic
        if temp_folder_localitate_med:
            folder_localitate_med = temp_folder_localitate_med
        if temp_folder_localitate_mare:
            folder_localitate_mare = temp_folder_localitate_mare

    # Generăm adresa
    adresa = f"Str. {strada} NR. {numar} LOC. {localitate} JUD. {judet}"
    if bloc:
        adresa += f" Bl. {bloc}"
    if scara:
        adresa += f" Sc. {scara}"
    if etaj:
        adresa += f" Et. {etaj}"
    if apartament:
        adresa += f" Ap. {apartament}"
    if cp:
        adresa += f" CP. {cp}"

    print(f"Rezultate procesare: {nume} {prenume}, {email}, {phone}, {adresa}")  # Debug: Afișăm rezultatele procesării

    # Nume fișier nou
    nume_fisier = os.path.basename(image_path)
    nume_fisier_nou = f"{nume} {prenume}.jpg"

    # Creează folderele pentru localitate (mare, mediu, mic)
    create_folder_hierarchy(output_folder, folder_localitate_mare, folder_localitate_med, folder_localitate_mic)

    # Creează calea completă a folderului de destinație
    # Pentru localități necunoscute, construim calea doar cu folderele care nu sunt goale
    path_parts = [output_folder]
    if folder_localitate_mare.strip():
        path_parts.append(folder_localitate_mare.strip())
    if folder_localitate_med.strip():
        path_parts.append(folder_localitate_med.strip())
    if folder_localitate_mic.strip():
        path_parts.append(folder_localitate_mic.strip())
    
    folder_localitate = os.path.join(*path_parts)
    
    # Verifică dacă fișierul există și adaugă număr secvențial dacă e necesar
    nume_fisier_final = nume_fisier_nou
    fisier_txt_final = f"{nume} {prenume}.txt"
    counter = 1
    
    while os.path.exists(os.path.join(folder_localitate, nume_fisier_final)) or os.path.exists(os.path.join(folder_localitate, fisier_txt_final)):
        counter += 1
        nume_fisier_final = f"{nume} {prenume} {counter}.jpg"
        fisier_txt_final = f"{nume} {prenume} {counter}.txt"
    
    # Mutăm și redenumim imaginea cu numele final
    noua_cale_imagine = os.path.join(folder_localitate, nume_fisier_final)
    shutil.move(image_path, noua_cale_imagine)

    # Creează fișierul text cu numele final
    fisier_txt = os.path.join(folder_localitate, fisier_txt_final)
    with open(fisier_txt, 'w', encoding='utf-8') as f:
        f.write(f"{nume}\n{initiala_tatalui}\n{prenume}\n{cnp_total}\n{adresa}\n{phone}\n{email}\n{doiani}")
    
    # Adăugăm imediat înregistrarea în Excel
    try:
        from src.excel.excel_manager import add_single_person_to_excel
        add_single_person_to_excel(output_folder, fisier_txt)
    except Exception as e:
        print(f"Eroare la adăugarea în Excel: {e}")
    
    # Returnăm CNP-ul extras pentru validare în fluxul principal
    return cnp_total

def create_folder_hierarchy(output_folder, folder_localitate_mare, folder_localitate_med, folder_localitate_mic):
    # Creează folderele pentru localitate și subfolderele corespunzătoare
    # Pentru localități necunoscute, doar folder_localitate_mare va fi setat
    
    if not folder_localitate_mare.strip():
        print("Eroare: folder_localitate_mare este gol!")
        return
    
    folder_localitate_mare_path = os.path.join(output_folder, folder_localitate_mare.strip())
    
    # Verifică dacă avem nivele suplimentare de foldere
    if folder_localitate_med.strip():
        folder_localitate_med_path = os.path.join(folder_localitate_mare_path, folder_localitate_med.strip())
        if folder_localitate_mic.strip():
            folder_localitate_mic_path = os.path.join(folder_localitate_med_path, folder_localitate_mic.strip())
            os.makedirs(folder_localitate_mic_path, exist_ok=True)
        else:
            os.makedirs(folder_localitate_med_path, exist_ok=True)
    else:
        print(f"Creăm doar folderul principal: {folder_localitate_mare_path}")
        os.makedirs(folder_localitate_mare_path, exist_ok=True)

    # print(f"Folderele au fost create sau există deja.")  # Comentat pentru a reduce output-ul
