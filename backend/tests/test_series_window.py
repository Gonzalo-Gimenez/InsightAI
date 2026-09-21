from datetime import date
from unittest.mock import patch

from app.services.nortec_analytics import default_period, months_back, series_window


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


def test_months_back_doce_meses():
    assert months_back(date(2026, 9, 30), 12, date(2024, 3, 1)) == date(2025, 10, 1)


@patch("app.services.nortec_analytics.date_bounds")
def test_default_period_son_doce_meses(mock_bounds):
    mock_bounds.return_value = (date(2024, 3, 1), date(2026, 9, 30))
    desde, hasta = default_period()
    assert desde == date(2025, 10, 1)
    assert hasta == date(2026, 9, 30)
