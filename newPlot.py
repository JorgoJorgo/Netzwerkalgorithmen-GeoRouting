import matplotlib.pyplot as plt
import numpy as np


def move_square_one_to_end(file_path):
    try:
        # Datei öffnen und alle Zeilen lesen
        with open(file_path, 'r') as file:
            lines = file.readlines()

        # Index der Zeilen mit 'SquareOne FR2' finden
        square_one_indices = [i for i, line in enumerate(lines) if 'SquareOne FR2' in line]

        # Verschiebe die gefundenen Zeilen ans Ende der Liste
        for index in square_one_indices[::-1]:
            lines.append(lines.pop(index))

        # Schreibe die aktualisierten Zeilen zurück in die Datei
        with open(file_path, 'w') as file:
            file.writelines(lines)

        print(f'Die Zeilen mit "SquareOne FR2" wurden erfolgreich ans Ende der Datei verschoben: {file_path}')

    except FileNotFoundError:
        print(f'Die Datei wurde nicht gefunden: {file_path}')
    except Exception as e:
        print(f'Ein Fehler ist aufgetreten: {e}')

def calculate_algorithm_metrics(file_path):
    try:
        # Datei öffnen und alle Zeilen lesen
        with open(file_path, 'r') as file:
            lines = file.readlines()

        # Überspringe die ersten zwei Zeilen (Kommentare und Datum)
        data_lines = lines[2:]

        # Initialisiere leere Dictionaries für success und hops pro Algorithmus
        success_dict = {}
        hops_dict = {}

        # Iteriere über die Datenzeilen und summiere success und hops pro Algorithmus
        for line in data_lines:
            # Splitte die Zeile
            parts = line.strip().split(', ')

            # Extrahiere Algorithmus, success und hops
            algorithm = parts[3]
            success = float(parts[8])
            hops = int(parts[7])

            # Summiere die Werte für jeden Algorithmus
            if algorithm in success_dict:
                success_dict[algorithm] += success
                hops_dict[algorithm] += hops
            else:
                success_dict[algorithm] = success
                hops_dict[algorithm] = hops

        # Gebe die Ergebnisse aus
        print("Erfolg und Hops pro Algorithmus:")
        for algorithm in success_dict:
            average_success = success_dict[algorithm] / (len(data_lines) /2)
            average_hops = hops_dict[algorithm] / (len(data_lines)/2)
            print(f"{algorithm}: Durchschnittlicher Erfolg = {average_success:.2f}, Durchschnittliche Hops = {average_hops:.2f}")
            
        print("##################################")
    except FileNotFoundError:
        print(f'Die Datei wurde nicht gefunden: {file_path}')
    except Exception as e:
        print(f'Ein Fehler ist aufgetreten: {e}')

# Beispielaufruf mit dem Dateipfad
files =[
    'results/benchmark-faces-random-all-multiple-trees-10-3.txt',
    'results/benchmark-faces-random-all-multiple-trees-12-3.txt',
    'results/benchmark-faces-random-all-multiple-trees-14-3.txt',
    'results/benchmark-faces-random-all-multiple-trees-16-3.txt',
    'results/benchmark-faces-random-all-multiple-trees-18-3.txt',
    'results/benchmark-faces-random-all-multiple-trees-20-3.txt',
    'results/benchmark-faces-random-all-multiple-trees-22-3.txt',
    'results/benchmark-faces-random-all-multiple-trees-24-3.txt',
    'results/benchmark-faces-random-all-multiple-trees-26-3.txt',
    'results/benchmark-faces-random-all-multiple-trees-28-3.txt',
    'results/benchmark-faces-random-all-multiple-trees-30-3.txt',
    'results/benchmark-faces-random-all-multiple-trees-32-3.txt',
    'results/benchmark-faces-random-all-multiple-trees-34-3.txt',
    'results/benchmark-faces-random-all-multiple-trees-36-3.txt',
    'results/benchmark-faces-random-all-multiple-trees-38-3.txt',
    'results/benchmark-faces-random-all-multiple-trees-40-3.txt'
]


#move_square_one_to_end(file_path)


for file_path in files:
    
    calculate_algorithm_metrics(file_path)


# Success Rate SquareOne
successSquareOne = []

# Success Rate Faces
successFaces = []

# Hops SquareOne
hopsSquareOne = []

# Hops Faces
hopsFaces = []

#Faces Success: 
successFaces = [1.0,0.98, 0.98, 0.92, 1.0, 0.98, 1.0, 0.96, 0.98, 1.0, 0.98, 0.94, 0.94, 0.94, 0.98, 0.98]

#Faces Hops:
hopsFaces = [7.5,11.10,11.10,12.60,14.20,14.20,16.50,16.80,17.30,17.40,16.70,19.50,22.0,21.20,18.40,21.70] 

#SquareOne Success:
successSquareOne = [1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0]

#SquareOne Hops:
hopsSquareOne = [3.0,3.1,3.8,4.0,4.5,4.5,4.6,5.1,5.3,5.8,6.1,6.6,6.4,6.8,6.7,6.8]

# x-Werte von 10 bis 40 in 2er-Schritten
x_values = np.arange(10, 41, 2)

# Plot der Daten
plt.plot(x_values, hopsSquareOne, label='hopsSquareOne', marker='o')
plt.plot(x_values, hopsFaces, label='hopsFaces', marker='o')

# Diagrammtitel und Achsentitel
plt.title('Durchschnittliche Hops bei randomisierten planaren Graphen')
plt.xlabel('Graphengröße')
plt.ylabel('Durchschnittliche Hops')

# Legende anzeigen
plt.legend()

# Diagramm anzeigen
plt.show()


# x-Werte von 10 bis 40 in 2er-Schritten
x_values = np.arange(10, 41, 2)

# Plot der Daten
plt.plot(x_values, successSquareOne, label='successSquareOne', marker='o')
plt.plot(x_values, successFaces, label='successFaces', marker='o')

# Diagrammtitel und Achsentitel
plt.title('Erfolgsrate bei randomisierten planaren Graphen')
plt.xlabel('Graphengröße')
plt.ylabel('Erfolgsrate')

# Legende anzeigen
plt.legend()

# Diagramm anzeigen
plt.show()