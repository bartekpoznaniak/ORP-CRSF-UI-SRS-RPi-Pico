#!/bin/bash

# Sprawdzenie czy podano rozszerzenie
if [ -z "$1" ]; then
    echo "Użycie: $0 <rozszerzenie> [plik_wyjsciowy]"
    echo "Przykład: $0 py caly_projekt.txt"
    exit 1
fi

EXT=$1
OUTPUT=${2:-"skonsolidowany_kod.txt"}

# Czyszczenie pliku wyjściowego, jeśli istnieje
> "$OUTPUT"

echo "Rozpoczynam łączenie plików .$EXT do $OUTPUT..."

# Szukanie plików (z pominięciem samego pliku wyjściowego)
find . -type f -name "*.$EXT" ! -name "$OUTPUT" | while read -r file; do
    echo "Dodaję: $file"
    echo "================================================================" >> "$OUTPUT"
    echo "PLIK: $file" >> "$OUTPUT"
    echo "================================================================" >> "$OUTPUT"
    echo "" >> "$OUTPUT"
    
    cat "$file" >> "$OUTPUT"
    
    echo "" >> "$OUTPUT"
    echo -e "\n" >> "$OUTPUT" # Dodatkowe linie odstępu między plikami
done

echo "Gotowe! Cały kod znajduje się w: $OUTPUT"
