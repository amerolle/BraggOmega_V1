
from windfreak import SynthHD

# Initialisation du synthétiseur sur le port COM4
synth = SynthHD('COM4')

# Sélectionner et configurer le canal 0
synth.write("channel", 0)  # Sélection du canal 0
synth.write("sweep_freq_low", 750)    
synth.write("sweep_freq_high", 3000)  
synth.write("sweep_freq_step", 0.1)     
synth.write("sweep_power_low", 10)      
synth.write("sweep_power_high", 10)     

# Sélectionner et configurer le canal 1
synth.write("channel", 1)  # Sélection du canal 1
synth.write("sweep_freq_low", 750)   
synth.write("sweep_freq_high", 3000)  
synth.write("sweep_freq_step", 0.1)
synth.write("sweep_power_low", 8)  
synth.write("sweep_power_high", 8)  

# Configuration du balayage différentiel (s'applique à l'ensemble du balayage)
synth.write("sweep_diff_meth", 1)  # Active le balayage différentiel
synth.write("sweep_diff_freq", 5)  # Définit la fréquence différentielle à 5 MHz

# Activer le balayage continu (uniquement après avoir configuré tout)
synth.sweep_enable = True
def safe_read(command):
    """Lit une valeur du synthétiseur et gère les erreurs"""
    try:
        if command in synth.API.keys():
            value = synth.read(command)
            print(f"{command} = {value}")  # Debug
            return value
        else:
            print(f"⚠ Commande non supportée: {command}")
            return None
    except Exception as e:
        print(f"❌ Erreur lors de la lecture de {command} : {str(e)}")
        return None

# 🔹 Sélectionner et configurer le canal 0
synth.write("channel", 0)
print("\n📌 Configuration du canal 0 :")
print("Fréquence basse :", safe_read("sweep_freq_low"))
print("Fréquence haute :", safe_read("sweep_freq_high"))
print("Pas de balayage :", safe_read("sweep_freq_step"))
print("Puissance basse :", safe_read("sweep_power_low"))
print("Puissance haute :", safe_read("sweep_power_high"))

# 🔹 Sélectionner et configurer le canal 1
synth.write("channel", 1)
print("\n📌 Configuration du canal 1 :")
print("Fréquence basse :", safe_read("sweep_freq_low"))
print("Fréquence haute :", safe_read("sweep_freq_high"))
print("Pas de balayage :", safe_read("sweep_freq_step"))
print("Puissance basse :", safe_read("sweep_power_low"))
print("Puissance haute :", safe_read("sweep_power_high"))

# 🔹 Lire les paramètres du sweep différentiel
print("\n📌 Sweep différentiel :")
print("Méthode de sweep différentiel :", safe_read("sweep_diff_meth"))
print("Fréquence différentielle :", safe_read("sweep_diff_freq"))

# 🔹 Lire l'état du sweep
print("\n📌 État du balayage :")
print("Balayage activé :", safe_read("sweep_cont"))