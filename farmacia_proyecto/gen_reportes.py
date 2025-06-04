from collections import Counter
import datos_compartidos as db

def generar_reporte_mensual():

    print("\n --- Servicio: Generación de reporte mensual ---")
    if db.ventas_db and not db.compras_db:
        print("No hay datos de ventas ni compras para generar reportes.")
        return {"estado": "fallido", "mensaje": "No hay datos para reportar."}
    
    while True:
        try:
            anio = int(input("ingrese el año del reporte: "))
            if 2000 < anio < 2100:
                break
            else:
                print("Año Inválido.")
        except ValueError:
            print("Entrada Inválida. Ingrese un número para el año.")

    while True:
        try:
            mes = int(input("Ingrese un mes del año (1-12): "))
            if 1 <= mes <= 12:
                break
            else:
                print ("Ingrese un mes válido")
        except ValueError:
            print("Entrada Inválida. Ingrese un número para el mes.")

    mes_anio_filtro = f"{anio}-{mes:02d}"
    print(f"\n --- Reporte para {mes_anio_filtro} ---")

    #Inicializacion del reporte
    reporte_datos = {
        "periodo": mes_anio_filtro,
        "ventas": {"monto_total": 0, "cantidad_prodcutos": 0, "top3_vendidos_nombres": []},
        "compras": {"monto_total": 0, "cantidad_productos": 0, "top3_compras_nombres": []},
        "ganancia_estimada": 0
    }

    #Registro de ventas
    ventas_mes = [v for v in db.ventas_db if v['fecha'].startswith(mes_anio_filtro)]
    reporte_datos["ventas"]["monto_total"] = sum(v['total_venta_final'] for v in ventas_mes)

    ids_ventas_mes = [v['id_venta'] for v in ventas_mes]
    detalles_venta_mes = [d for d in db.detalle_ventas_db if d['id_venta'] in ids_ventas_mes]

    reporte_datos["ventas"]["cantidad_productos"] = sum(d['cantidad'] for d in detalles_venta_mes)

    contador_productos_vendidos = Counter()
    for detalle in detalles_venta_mes:
        contador_productos_vendidos[detalle['codigo_producto']] += detalle['cantidad']

    top_3_vendidos = contador_productos_vendidos.most_common(3)
    reporte_datos["ventas"]["top3_vendidos_nombres"] = [f"{db.productos_db[cod]['nombre']}({cant}uds)" for cod, cant in top_3_vendidos]

    print("\n **Resumen de Ventas:**")
    if ventas_mes:
        print(f"Monto Total de Ventas: ${reporte_datos['ventas']['monto_total']:,}")
        print(f"Cantidad Total de Productos Vendidos: {reporte_datos['ventas']['cantidad_productos']}")
        print(f"Top 3 Productos Más Vedidos: {', '.join(reporte_datos['ventas']['top3_vendidos_nombres']) if reporte_datos['ventas']['top3_vendidos_nombres']else 'N/A'}")
    else:
        print("No se encontraron ventas para este período.")

    #Registro de compras
    compras_mes = [c for c in db.compras_db if c['fecha'].startswith(mes_anio_filtro)]
    reporte_datos["compras"]["monto_total"] = sum(c['total_compra'] for c in compras_mes)

    ids_compras_mes = [c['id_compra'] for c in compras_mes]
    detalles_compras_mes = [d for d in db.detalle_compras_db if d['id_compra'] in ids_compras_mes]

    reporte_datos["compras"]["cantidad_productos"] = sum(d['cantidad'] for d in detalles_compras_mes)

    contador_productos_comprados = Counter()
    for detalle in detalles_compras_mes:
        contador_productos_comprados[detalle['codigo_producto']] += detalle['cantidad']
        
    top_3_comprados = contador_productos_comprados.most_common(3)
    reporte_datos["compras"]["top_3_comprados_nombres"] = [f"{db.productos_db[cod]['nombre']} ({cant} uds)" for cod, cant in top_3_comprados]

    print("\n**Resumen de Compras:**")
    if compras_mes:
        print(f"Monto Total de Compras: ${reporte_datos['compras']['monto_total']:,}")
        print(f"Cantidad Total de Productos Comprados: {reporte_datos['compras']['cantidad_productos']}")
        print(f"Top 3 Productos Más Comprados: {', '.join(reporte_datos['compras']['top_3_comprados_nombres']) if reporte_datos['compras']['top_3_comprados_nombres'] else 'N/A'}")
    else:
        print("No se encontraron compras para este período.")
        
    reporte_datos["ganancia_estimada"] = reporte_datos["ventas"]["monto_total"] - reporte_datos["compras"]["monto_total"]
    print("\n**Resumen Financiero del Mes:**")
    print(f"Ganancia Total Estimada del Mes (Ventas - Compras): ${reporte_datos['ganancia_estimada']:,}")
    print("-----------------------------------")
    return {"estado": "exitoso", "reporte": reporte_datos}

if __name__ == "__main__":
    # Para probar, asegúrate de que haya datos en datos_compartidos.py
    # Puedes ejecutar los otros scripts primero para poblar los datos.
    print("Probando servicio de generación de reportes...")
    
    # Añadir algunos datos de prueba si es necesario para una ejecución aislada
    if not db.ventas_db:
         db.ventas_db.append({'id_venta': 'test_venta1', 'fecha': '2024-05-15', 'rut_trabajador': '33333333-3', 'rut_miembro': None, 'total_venta_bruto': 1200, 'puntos_usados': 0, 'total_venta_final': 1200})
         db.detalle_ventas_db.append({'id_detalle_venta': 'test_dv1', 'id_venta': 'test_venta1', 'codigo_producto': 'P001', 'cantidad': 1, 'precio_unitario': 1200})
    if not db.compras_db:
         db.compras_db.append({'id_compra': 'test_compra1', 'fecha': '2024-05-10', 'rut_trabajador': '33333333-3', 'total_compra': 700})
         db.detalle_compras_db.append({'id_detalle_compra': 'test_dc1', 'id_compra': 'test_compra1', 'codigo_producto': 'P001', 'cantidad': 1, 'precio_unitario': 700})

    resultado_reporte = generar_reporte_mensual()
    if resultado_reporte["estado"] == "exitoso":
        print("\nDatos del reporte generado (diccionario):")
        import json
        print(json.dumps(resultado_reporte["reporte"], indent=2))