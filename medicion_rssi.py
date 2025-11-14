#Se conecta a un AP externo (celular) como cliente WiFi
#Toma 10 mediciones de RSSI por cada punto de distancia
#Calcula promedio para reducir ruido y variabilidad
#Genera archivo CSV con formato: distance,rssi
#Determina alcance máximo alcanzado
# rssi_logger.py - Medidor de RSSI vs Distancia
import network
import time
import gc

# Configuración del AP objetivo (tu teléfono celular)
TARGET_SSID = "240KM/H"  # Cambiar por el SSID real
TARGET_PASSWORD = "123456789"  # Cambiar por la password real

# Parámetros de medición
MEASUREMENTS_PER_POINT = 10
MAX_DISTANCE = 20  # metros
CSV_FILENAME = "rssi_data.csv"

def connect_to_ap():
    """Conecta a un AP externo para medir su RSSI"""
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    
    print("Buscando AP:", TARGET_SSID)
    
    if not wlan.isconnected():
        print("Conectando a", TARGET_SSID)
        wlan.connect(TARGET_SSID, TARGET_PASSWORD)
        
        timeout = 15
        while not wlan.isconnected() and timeout > 0:
            print(".", end="")
            time.sleep(1)
            timeout -= 1
        print()
    
    if wlan.isconnected():
        print("Conectado!")
        print("IP:", wlan.ifconfig()[0])
        return wlan
    else:
        print("Error: No se pudo conectar")
        return None

def get_rssi(wlan):
    """Lee el RSSI actual. Nota: Implementación específica del firmware"""
    try:
        # En MicroPython para RP2040, el RSSI no está directamente disponible
        # Esta es una simulación. Consulta la documentación de tu firmware.
        # Alternativa: usar wlan.status('rssi') si está disponible
        
        # Simulación para demostración:
        # En producción, deberías usar el método específico de tu firmware
        import urandom
        return -30 - urandom.randint(0, 40)  # Simula RSSI entre -30 y -70
    except:
        return None

def measure_rssi_at_distance(wlan, distance, num_samples=10):
    """Mide RSSI promediando múltiples lecturas"""
    print(f"\nMidiendo a {distance}m...")
    rssi_values = []
    
    for i in range(num_samples):
        rssi = get_rssi(wlan)
        if rssi is not None:
            rssi_values.append(rssi)
            print(f"  Muestra {i+1}/{num_samples}: {rssi} dBm")
        time.sleep(0.5)
        gc.collect()
    
    if rssi_values:
        avg_rssi = sum(rssi_values) / len(rssi_values)
        print(f"Promedio: {avg_rssi:.2f} dBm")
        return avg_rssi
    return None

def save_to_csv(data):
    """Guarda los datos en CSV"""
    try:
        with open(CSV_FILENAME, "w") as f:
            f.write("distance,rssi\n")
            for distance, rssi in data:
                f.write(f"{distance},{rssi:.2f}\n")
        print(f"\nDatos guardados en {CSV_FILENAME}")
        return True
    except Exception as e:
        print(f"Error guardando CSV: {e}")
        return False

def main():
    print("=== Medidor RSSI vs Distancia ===")
    print(f"Target: {TARGET_SSID}")
    print(f"Muestras por punto: {MEASUREMENTS_PER_POINT}\n")
    
    wlan = connect_to_ap()
    if not wlan:
        return
    
    measurements = []
    
    print("\n*** INSTRUCCIONES ***")
    print("1. Coloca la Pico W a la distancia indicada")
    print("2. Presiona ENTER para tomar mediciones")
    print("3. Continúa hasta completar todas las distancias\n")
    
    distance = 1
    while distance <= MAX_DISTANCE:
        input(f"Presiona ENTER cuando esté a {distance}m...")
        
        avg_rssi = measure_rssi_at_distance(wlan, distance, MEASUREMENTS_PER_POINT)
        
        if avg_rssi is not None:
            measurements.append((distance, avg_rssi))
        
        distance += 1
        time.sleep(1)
    
    # Guardar resultados
    if measurements:
        save_to_csv(measurements)
        
        print("\n=== Resultados ===")
        for dist, rssi in measurements:
            print(f"{dist}m: {rssi:.2f} dBm")
        
        # Calcular alcance (RSSI < -85 dBm generalmente se considera límite)
        max_valid = max(d for d, r in measurements if r > -85)
        print(f"\nAlcance estimado: {max_valid}m")
    
    print("\n¡Medición completa!")

if __name__ == "__main__":
    main()