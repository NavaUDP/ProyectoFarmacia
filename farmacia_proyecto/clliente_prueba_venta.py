import socket

def send_request(service_name, payload):
    """
    Envía una petición al bus y recibe la respuesta.
    """
    HOST = 'localhost'
    PORT = 5000

    # Formato de la transacción: NNNNNSSSSS DATOS
    # NNNNN es el largo de SSSSS + DATOS
    message_body = f"{service_name}{payload}"
    header = f"{len(message_body):05d}"
    full_message = f"{header}{message_body}"

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        print(f"Enviando: {full_message}")
        s.connect((HOST, PORT))
        s.sendall(full_message.encode('utf-8'))
        
        # Recibir respuesta
        response_header = s.recv(5).decode('utf-8')
        if not response_header:
            print("No se recibió respuesta.")
            return

        response_len = int(response_header)
        response_data = s.recv(response_len).decode('utf-8')
        
        print("\n--- Respuesta del Servidor ---")
        print(f"Raw: {response_header}{response_data}")
        print(f"Servicio: {response_data[:5]}")
        print(f"Estado: {response_data[5:7]}")
        print(f"Datos: {response_data[7:]}")
        print("----------------------------\n")

if __name__ == "__main__":
    SERVICE_NAME = "serv2"
    
    # --- CASO 1: Venta exitosa a cliente miembro usando puntos ---
    print("--- PRUEBA 1: Venta exitosa a miembro usando puntos ---")
    # Vende 1 'Menta' (1200) y 2 'Crema' (900 c/u = 1800). Total bruto: 3000.
    # Usa 500 puntos. Total final: 2500. Gana 300 puntos (150*2).
    # Trabajador: 87654321 (operativo)
    # Cliente: 11222333
    payload_1 = "11222333;500;87654321;PROD0001,1;PROD0002,2"
    send_request(SERVICE_NAME, payload_1)
    
    input("Presiona Enter para continuar con la siguiente prueba...")

    # --- CASO 2: Venta fallida por falta de stock ---
    print("\n--- PRUEBA 2: Venta fallida por falta de stock ---")
    # Intenta vender 200 'Menta', pero el stock inicial es 100 (y ya vendimos 1).
    payload_2 = "None;None;87654321;PROD0001,200"
    send_request(SERVICE_NAME, payload_2)
    
    input("Presiona Enter para continuar con la siguiente prueba...")

    # --- CASO 3: Venta a cliente no miembro (público general) ---
    print("\n--- PRUEBA 3: Venta a público general ---")
    # Vende 10 'Vitaminas'. No hay cliente miembro ni uso de puntos.
    payload_3 = "None;None;87654321;PROD0003,10"
    send_request(SERVICE_NAME, payload_3)