from datetime import date

from app.services.nortec_analytics import months_back, series_window


def test_series_window_expande_un_mes():
    desde, hasta = series_window(date(2025, 8, 1), date(2025, 8, 31), date(2024, 3, 1))
    assert desde == date(2024, 9, 1)
    assert hasta == date(2025, 8, 31)


def test_series_window_respeta_minimo():
    desde, hasta = series_window(date(2025, 8, 1), date(2025, 8, 31), date(2025, 1, 1))
    assert desde == date(2025, 1, 1)
    assert hasta == date(2025, 8, 31)


def test_series_window_no_toca_rango_largo():
    desde, hasta = series_window(date(2024, 3, 1), date(2025, 8, 31), date(2024, 3, 1))
    assert desde == date(2024, 3, 1)
    assert hasta == date(2025, 8, 31)


def test_months_back_cinco_meses():
    assert months_back(date(2025, 8, 31), 5, date(2024, 3, 1)) == date(2025, 4, 1)


def test_series_window_expande_un_mes():
    desde, hasta = series_window(date(2025, 8, 1), date(2025, 8, 31), date(2024, 3, 1))
    assert desde == date(2024, 9, 1)
    assert hasta == date(2025, 8, 31)


def test_series_window_respeta_minimo():
    desde, hasta = series_window(date(2025, 8, 1), date(2025, 8, 31), date(2025, 1, 1))
    assert desde == date(2025, 1, 1)
    assert hasta == date(2025, 8, 31)


def test_series_window_no_toca_rango_largo():
    desde, hasta = series_window(date(2024, 3, 1), date(2025, 8, 31), date(2024, 3, 1))
    assert desde == date(2024, 3, 1)
    assert hasta == date(2025, 8, 31)
