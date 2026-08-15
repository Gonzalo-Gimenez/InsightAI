def total_ventas(data):
    return sum(item["ventas"] for item in data)


def promedio_ventas(data):
    if not data:
        return 0
    return total_ventas(data) / len(data)


def venta_maxima(data):
    if not data:
        return None
    return max(data, key=lambda item: item["ventas"])


def venta_minima(data):
    if not data:
        return None
    return min(data, key=lambda item: item["ventas"])


def ventas_por_categoria(data):
    categorias = {}
    for item in data:
        cat = item["categoria"]
        categorias[cat] = categorias.get(cat, 0) + item["ventas"]
    return categorias


def compute_metrics(data):
    return {
        "total_ventas": total_ventas(data),
        "promedio_ventas": promedio_ventas(data),
        "venta_maxima": venta_maxima(data),
        "venta_minima": venta_minima(data),
        "ventas_por_categoria": ventas_por_categoria(data),
    }