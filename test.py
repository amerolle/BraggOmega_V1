### TEST LASER
# from devices.MuquansLaser import MuquansLaser

# # Initialisation du laser
# laser = MuquansLaser(host="10.0.2.107", port=23)

# # Connexion au laser
# laser.connect()

# # Vérifier que la connexion est bien établie
# if laser.tn:
#     print("Connexion réussie au laser!")

#     # Allumer le seed laser
#     laser.seed_on()

#     # Régler la puissance EDFA à 1
#     laser.set_power(1)

#     # Déconnexion propre après usage
#     laser.disconnect()
# else:
#     print("Échec de la connexion au laser.")

### TEST RFgenerator
# import time
# from devices.RFGenerator import RFGenerator

# def test_rf_generator():
#     # Initialiser le générateur RF sur le port COM4 (ou ajuster selon votre configuration)
#     rf_gen = RFGenerator(port="COM4")

#     if rf_gen.synth is None:
#         print("Échec de la connexion au générateur RF. Vérifiez la connexion et le port série.")
#         return

#     try:
#         # Activer le canal 0
#         rf_gen.enable(0)
#         time.sleep(1)  # Attendre un peu pour vérifier que le canal est activé

#         # Définir la fréquence sur le canal 0
#         rf_gen.set_frequency(0, 10000000)  # Fréquence de 1000 MHz sur le canal 0
#         time.sleep(1)

#         # Définir la puissance sur le canal 0
#         rf_gen.set_power(0, 8)  # Puissance de 10 dBm sur le canal 0
#         time.sleep(1)

#         # Lire la fréquence et la puissance du canal 0 pour vérification
#         rf_gen.read_parameter(0, "frequency")
#         rf_gen.read_parameter(0, "power")
        
#         # Configurer un balayage différentiel
#         rf_gen.configure_differential_sweep(
#             f_low=750, f_high=3000, f_step=0.1, diff_freq=5, step_time=0.1, trigger_mode="full_sweep"
#         )
#         time.sleep(1)

#         # Activer le balayage continu
#         rf_gen.enable_sweep(True)
#         time.sleep(2)

#         # Désactiver le balayage continu
#         #rf_gen.enable_sweep(False)
#         time.sleep(1)

#         # Désactiver les deux canaux
#         # rf_gen.disable(0)
#         # rf_gen.disable(1)
#         time.sleep(1)

#     except Exception as e:
#         print(f"Une erreur s'est produite : {e}")
    
#     # Finaliser l'arrêt du générateur RF
#     #rf_gen.shutdown()

# # Lancer le test
# test_rf_generator()

#### TEST Wavemeter
from devices.WaveMeter import Wavemeter
from devices.TektroAFG import TektronixAFG3000C
import time
import requests



class ExperimentController:
    """
    Contrôle l'expérience en utilisant uniquement le Wavemeter et le Tektronix AFG3000C.
    """
    def __init__(self, afg_ip="192.168.0.143", wavemeter_url="http://localhost:5000"):
        """Initialisation des appareils"""
        print("Initialisation des appareils...")

        # Initialisation du générateur de signal Tektronix AFG3000C
        self.signal_gen = TektronixAFG3000C(ip=afg_ip)
        print("✅ Tektronix AFG3000C initialisé.")

        # Initialisation du Wavemeter
        self.wavemeter = Wavemeter(base_url=wavemeter_url)
        print("✅ Wavemeter initialisé.")

    def connect_all(self):
        """Connexion aux appareils."""
        print("\nConnexion aux appareils...")
        try:
            self.signal_gen.connect()
            print("✅ Tektronix AFG3000C connecté.")
        except Exception as e:
            print(f"⚠️ Erreur connexion AFG: {e}")

    def run_experiment(self, num_steps=5, delay=1):
        """
        Exécute l'expérience en ajustant la tension et en mesurant la fréquence du laser.
        """
        print("\nDébut de l'expérience...")
        results = []

        # Génération des tensions
        voltage_values = [(step / (num_steps - 1)) * 1.8 for step in range(num_steps)] if num_steps > 1 else [0]

        try:
            for step, voltage in enumerate(voltage_values):
                print(f"\n--- Étape {step+1}/{num_steps} ---")
                # Appliquer la tension au générateur de signal
                self.signal_gen.set_dc_voltage(voltage)
                try:
                    response = requests.get("http://localhost:5000/api/freq/0", timeout=5)
                    print(f"Réponse brute du Wavemeter : {response.text}")  # Ajoute ce print
                    freq = response.json()
                    
                except Exception as e:
                    print(f"⚠️ Erreur de connexion au Wavemeter : {e}")
                # Stocker les résultats
                results.append({
                    "step": step + 1,
                    "voltage": voltage,
                    "laser_frequency": freq
                })

                # Attente avant la prochaine mesure
                time.sleep(delay)

        except Exception as e:
            print(f"⚠️ Erreur pendant l'expérience : {e}")
        finally:
            print("\nExpérience terminée.")

        return results

    def shutdown(self):
        """Arrêt du générateur de signal."""
        self.signal_gen.disconnect()
        print("\nArrêt des appareils...")
    


if __name__ == "__main__":
    # Création de l'objet de l'expérience avec Wavemeter et AFG
    exp = ExperimentController()

    # Connexion aux appareils
    exp.connect_all()

    # Exécution de l'expérience
    results = exp.run_experiment(num_steps=5, delay=2)

    # Affichage des résultats
    for r in results:
        print(f"Étape {r['step']}: Tension = {r['voltage']} V, Fréquence Laser = {r['laser_frequency']} THz")

    # Arrêt des appareils
    exp.shutdown()



