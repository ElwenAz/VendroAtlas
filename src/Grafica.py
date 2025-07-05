import flet as ft
import asyncio
import random
from db_connection import create_connection, close_connection
from datetime import datetime, timedelta
import numpy as np

def obtener_ganancias_semana():
    connection = create_connection()
    if not connection:
        print("No se pudo conectar a la base de datos.")
        return [], {}

    try:
        hoy = datetime.now().date()
        lunes = hoy - timedelta(days=hoy.weekday())
        domingo = lunes + timedelta(days=6)

        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT nombre FROM productos")
        todos_los_productos = [row["nombre"] for row in cursor.fetchall()]

        query_ventas = """
            SELECT p.nombre AS producto, DATE(v.fecha_venta) as fecha, 
                v.cantidad_kg, v.precio_kg,
                SUM(v.cantidad_kg * v.precio_kg) as total_ventas
            FROM ventas v
            JOIN productos p ON v.id_producto = p.id_producto
            WHERE v.fecha_venta BETWEEN %s AND %s
            GROUP BY p.nombre, DATE(v.fecha_venta), v.cantidad_kg, v.precio_kg
        """

        query_compras = """
            SELECT p.nombre AS producto, DATE(c.fecha_compra) as fecha, 
            c.cantidad_kg, c.precio_kg,
            (c.cantidad_kg * c.precio_kg) as total_compras
            FROM compras c
            JOIN productos p ON c.id_producto = p.id_producto
            WHERE c.fecha_compra BETWEEN %s AND %s
            AND c.nombre_usuario != 'TRANSFERENCIA'
            ORDER BY c.fecha_compra DESC
        """

        cursor.execute(query_ventas, (lunes, domingo))
        ventas = cursor.fetchall()
        cursor.execute(query_compras, (lunes, domingo))
        compras = cursor.fetchall()

        historial=[]
        for v in ventas:
            historial.append({
                "tipo": "venta",
                "producto": v["producto"],
                "fecha": v["fecha"],
                "kilos": float(v["cantidad_kg"]),
                "precio": float(v["precio_kg"]),
                "total": float(v["total_ventas"])
            })

        for c in compras:
            historial.append({
                "tipo": "compra",
                "producto": c["producto"],
                "fecha": c["fecha"],
                "kilos": float(c["cantidad_kg"]),
                "precio": float(c["precio_kg"]),
                "total": float(c["total_compras"])
            })

        historial.sort(key=lambda h: h["fecha"], reverse=True)

        # PROCESAR DÍAS DE LA SEMANA
        dias = [(lunes + timedelta(days=i)).strftime("%d/%m") for i in range(7)]

        productos = set(todos_los_productos)

        movimientos = {p: [0]*7 for p in productos}

        for v in ventas:
            idx = (datetime.strptime(str(v["fecha"]), "%Y-%m-%d").date() - lunes).days
            if 0 <= idx < 7:
                movimientos[v["producto"]][idx] += float(v["total_ventas"])

        for c in compras:
            idx = (datetime.strptime(str(c["fecha"]), "%Y-%m-%d").date() - lunes).days
            if 0 <= idx < 7:
                movimientos[c["producto"]][idx] -= float(c["total_compras"])

        # CALCULAR ACUMULADO DÍA A DÍA
        ganancias = {p: [0]*7 for p in productos}
        for p in productos:
            for i in range(7):
                if i == 0:
                    ganancias[p][i] = movimientos[p][i]
                else:
                    ganancias[p][i] = ganancias[p][i-1] + movimientos[p][i]
        print("VENTAS:", ventas)
        print("COMPRAS:", compras)

        return dias, ganancias, historial
    except Exception as ex:
        print(f"Error al obtener ganancias: {ex}")
        return [], {}
    finally:
        close_connection(connection)

def color_aleatorio():
    return "#{:06x}".format(random.randint(0, 0xFFFFFF))


def main(page: ft.Page, regresar_callback):
    page.title = "Sistema de Ganancias"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = (20, 20, 30, 20)

    dias, ganancias, historial = obtener_ganancias_semana()
    productos = list(ganancias.keys())

    colores = {p: color_aleatorio() for p in productos}

    checks = {p: ft.Checkbox(label=p, value=True, fill_color=colores[p]) for p in productos}

    # CALCULA EL MÍNIMO Y MÁXIMO DE LAS GANANCIAS PARA EJE Y
    valores = [valor for lista in ganancias.values() for valor in lista]
    if valores:
        min_y = min(valores)
        max_y = max(valores)
        if min_y == max_y:
            min_y -= 5
            max_y += 5
        y_labels = np.linspace(min_y, max_y, 8)
    else:
        y_labels = np.linspace(0, 10, 8)

    chart = ft.LineChart(
        width=950,
        interactive=True,
        height=350,
        left_axis=ft.ChartAxis(
            labels=[ft.ChartAxisLabel(float(v), ft.Text(f"${v:.2f}")) for v in y_labels],
            labels_size=40
        ),
    )

    chart.bottom_axis = ft.ChartAxis(
        labels=[ft.ChartAxisLabel(i, ft.Text(dias[i], size=10, rotate=-45)) for i in range(len(dias))],
        labels_size=60,
        labels_interval=1
    )

    def update_chart(e=None):
        selected = [p for p, cb in checks.items() if cb.value]
        chart.data_series = []
        chart.bottom_axis = ft.ChartAxis(
            labels=[ft.ChartAxisLabel(i, ft.Text(dias[i])) for i in range(len(dias))],
            labels_size=40
        )
        for producto in selected:
            chart.data_series.append(
                ft.LineChartData(
                    data_points=[ft.LineChartDataPoint(i, ganancias[producto][i]) for i in range(len(dias))],
                    stroke_width=3,
                    color=colores[producto],
                    curved=False,
                    below_line_bgcolor=ft.Colors.with_opacity(0.1, colores[producto])
                )
            )
        chart.update()

    panel_seleccion = ft.Container(
        ft.Column(
            [
                ft.Text("SELECCIONAR PRODUCTOS", weight=ft.FontWeight.BOLD),
                *[checks[p] for p in productos],
                ft.Divider(),
                ft.Text("RESUMEN SEMANAL", weight=ft.FontWeight.BOLD),
                *[
                    ft.Row([
                        ft.Icon(name=ft.Icons.CIRCLE, color=colores[p], size=12),
                        ft.Text(p + ":", width=100),
                        ft.Text(f"${ganancias[p][-1]:.2f}", color="green")
                    ], spacing=5)
                    for p in productos
                ],
                ft.Divider(),
                ft.Row([
                    ft.Text("TOTAL:", weight=ft.FontWeight.BOLD),
                    ft.Text(
                        f"${sum(ganancias[p][-1] for p in productos):.2f}",
                        weight=ft.FontWeight.BOLD, color="green"
                    )
                ])
            ],
            spacing=8,
            scroll=ft.ScrollMode.ALWAYS,
            expand=True,
        ),
        width=250, 
        padding=10,
        bgcolor=ft.Colors.GREY_100,
        border_radius=10,
        margin=ft.Margin(right=0, bottom=20, top=0, left=0)
    )

    def recargar_historial():
        nonlocal dias, ganancias, historial, productos, colores, checks, tabla_historial
        dias, ganancias, historial = obtener_ganancias_semana()
        productos = list(ganancias.keys())
        colores = {p: color_aleatorio() for p in productos}
        checks = {p: ft.Checkbox(label=p, value=True, fill_color=colores[p]) for p in productos}
        tabla_historial.rows = [
            ft.DataRow(
                cells=[
                    ft.DataCell(ft.Text(
                        h["producto"],
                        color=colores.get(h["producto"], "#000")
                    )),
                    ft.DataCell(ft.Text(h["fecha"].strftime("%d/%m/%Y"))),
                    ft.DataCell(ft.Text(
                        f"{h['kilos']:.2f} kg" if isinstance(h["kilos"], (int, float)) else str(h["kilos"])
                    )),
                    ft.DataCell(ft.Text(
                        f"${h['precio']:.2f}" if isinstance(h["precio"], (int, float)) else str(h["precio"])
                    )),
                    ft.DataCell(ft.Text(
                        f"${h['total']:.2f}",
                        color="green" if h["tipo"] == "venta" else "red"
                    )),
                ]
            ) for h in historial
        ]
        page.update()


    tabla_historial = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("Producto", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("Fecha", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("Kilos", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("Precio/kg", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("Total", weight=ft.FontWeight.BOLD)),
        ],
        rows=[
            ft.DataRow(
                cells=[
                    ft.DataCell(ft.Text(
                        h["producto"],
                        color=colores.get(h["producto"], "#000")
                    )),
                    ft.DataCell(ft.Text(h["fecha"].strftime("%d/%m/%Y"))),
                    ft.DataCell(ft.Text(
                        f"{h['kilos']:.2f} kg" if isinstance(h["kilos"], (int, float)) else str(h["kilos"])
                    )),
                    ft.DataCell(ft.Text(
                        f"${h['precio']:.2f}" if isinstance(h["precio"], (int, float)) else str(h["precio"])
                    )),
                    ft.DataCell(ft.Text(
                        f"${h['total']:.2f}",
                        color="green" if h["tipo"] == "venta" else "red"
                    )),
                ]
            ) for h in historial
        ],
        vertical_lines=ft.border.BorderSide(1, ft.Colors.GREY_300),
        horizontal_lines=ft.border.BorderSide(1, ft.Colors.GREY_300),
    )

    def regresar(e):
        regresar_callback()

    # VISTA PRINCIPAL DE LA GRÁFICA
    page.views.append(
        ft.View(
            "/ganancias",
            [
                ft.Stack(
                    [
                        ft.Column(
                            [
                                ft.Row(
                                    [
                                        panel_seleccion,
                                        ft.VerticalDivider(width=1, color=ft.Colors.GREY_400),
                                        ft.Column(
                                            [
                                                ft.Text("HISTORIAL DE REPOSICIÓN", weight=ft.FontWeight.BOLD),
                                                ft.Container(
                                                    ft.Column([tabla_historial], scroll=ft.ScrollMode.ALWAYS),
                                                    height=250,
                                                    border_radius=10
                                                ),
                                                ft.Divider(height=20),
                                                ft.Text("GANANCIAS POR PRODUCTO", weight=ft.FontWeight.BOLD),
                                                ft.Container(
                                                    chart,
                                                    padding=0,
                                                    margin=ft.Margin(bottom=0, top=0, left=30, right=30),
                                                )
                                            ],
                                            spacing=10,
                                            expand=True,
                                        )
                                    ],
                                    spacing=20,
                                    expand=True,
                                ),
                            ],
                            expand=True,
                        ),
                        ft.Row(
                            [
                                ft.Container(
                                    ft.IconButton(
                                        icon=ft.Icons.ARROW_BACK,
                                        on_click=regresar,
                                    ),
                                    bgcolor="#EAEBE8",
                                    border_radius=ft.border_radius.all(5),
                                    padding=5,
                                    margin=ft.Margin(top=10, right=10, left=0, bottom=0),
                                )
                            ],
                            alignment=ft.MainAxisAlignment.END,
                            vertical_alignment=ft.CrossAxisAlignment.START,
                            expand=False
                        ),
                    ],
                    expand=True,
                )
            ],
            padding=0,
        )
    )

    page.update()

    # INICIALIZAR GRÁFICA
    async def delayed_update_chart():
        await asyncio.sleep(0.05)
        update_chart()
    page.run_task(delayed_update_chart)

    for cb in checks.values():
        cb.on_change = update_chart

        